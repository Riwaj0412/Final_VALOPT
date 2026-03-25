import mmap
import ctypes
import ctypes.wintypes
import time
import threading
import statistics
import psutil
from collections import deque
from dataclasses import dataclass
from typing import Optional


_VALO_EXE = "VALORANT-Win64-Shipping.exe"
_RTSS_EXE = "RTSS.exe"
_SHM_NAME = "RTSSSharedMemoryV2"

# ── RTSS shared memory C structs (from RTSS SDK) ──────────────────────────────


class RTSSSharedMemoryHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("dwSignature",    ctypes.c_uint32),   # 'RTSS' = 0x53535452
        ("dwVersion",      ctypes.c_uint32),   # version * 0x10000
        ("dwAppEntrySize", ctypes.c_uint32),   # sizeof one app entry
        ("dwAppArrOffset", ctypes.c_uint32),   # offset to app array
        ("dwAppArrSize",   ctypes.c_uint32),   # number of app entries
        ("dwOSDEntrySize", ctypes.c_uint32),
        ("dwOSDArrOffset", ctypes.c_uint32),
        ("dwOSDArrSize",   ctypes.c_uint32),
        ("dwOSDFrame",     ctypes.c_uint32),
    ]


class RTSSAppEntry(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("dwProcessID",  ctypes.c_uint32),
        ("szName",       ctypes.c_char * 260),
        ("dwFlags",      ctypes.c_uint32),
        ("dwTime0",      ctypes.c_uint32),
        ("dwTime1",      ctypes.c_uint32),
        ("dwFrames",     ctypes.c_uint32),
        # avg frame time in microseconds
        ("dwFrameTime",  ctypes.c_uint32),
        ("dwOSDX",       ctypes.c_uint32),
        ("dwOSDY",       ctypes.c_uint32),
        ("dwOSDPixel",   ctypes.c_uint32),
        ("dwOSDColor",   ctypes.c_uint32),
        ("dwOSDFrame",   ctypes.c_uint32),
        ("szOSD",        ctypes.c_char * 256),
        ("szOSDOwner",   ctypes.c_char * 256),
        # Extended fields (v2.3+)
        ("dwAvgFrameTime",    ctypes.c_uint32),
        ("dwAvgFPS",          ctypes.c_uint32),
        ("dwInstantaneousFPS", ctypes.c_uint32),
    ]


_RTSS_SIGNATURE = 0x53535452


# ── helpers ────────────────────────────────────────────────────────────────────
def is_valorant_running() -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] == _VALO_EXE:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def is_rtss_running() -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] == _RTSS_EXE:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def _open_rtss_shm():
    """Open RTSS shared memory. Returns mmap object or None."""
    try:
        INVALID_HANDLE = ctypes.c_void_p(-1).value
        PAGE_READONLY = 0x02
        FILE_MAP_READ = 0x0004

        kernel32 = ctypes.windll.kernel32
        h = kernel32.OpenFileMappingW(
            FILE_MAP_READ, False,
            ctypes.c_wchar_p(_SHM_NAME))

        if not h or h == INVALID_HANDLE:
            return None

        size = ctypes.sizeof(RTSSSharedMemoryHeader) + \
            256 * ctypes.sizeof(RTSSAppEntry)
        buf = kernel32.MapViewOfFile(h, FILE_MAP_READ, 0, 0, size)
        kernel32.CloseHandle(h)

        if not buf:
            return None
        return buf

    except Exception:
        return None


def _read_valo_fps(buf_ptr) -> Optional[float]:
    try:
        hdr = RTSSSharedMemoryHeader.from_address(buf_ptr)

        if hdr.dwSignature != _RTSS_SIGNATURE:
            return None
        if hdr.dwVersion < 0x00020000:
            return None

        entry_size = hdr.dwAppEntrySize
        arr_offset = hdr.dwAppArrOffset
        arr_size = hdr.dwAppArrSize

        for i in range(arr_size):
            addr = buf_ptr + arr_offset + i * entry_size
            try:
                entry = RTSSAppEntry.from_address(addr)
            except Exception:
                continue

            name = entry.szName.decode("utf-8", errors="ignore").lower()
            if "valorant" not in name and "win64-shipping" not in name:
                continue

            if entry.dwInstantaneousFPS > 0:
                return round(entry.dwInstantaneousFPS / 1000.0, 1)
            if entry.dwAvgFPS > 0:
                return round(entry.dwAvgFPS / 1000.0, 1)
            if entry.dwFrameTime > 0:
                return round(1_000_000.0 / entry.dwFrameTime, 1)

        return None

    except Exception:
        return None


# ── internal state ─────────────────────────────────────────────────────────────
_buf:       deque = deque(maxlen=100_000)
_capturing: bool = False
_stop_evt:  Optional[threading.Event] = None
_thread:    Optional[threading.Thread] = None
_lock:      threading.Lock = threading.Lock()
_source:    str = "none"


@dataclass
class FpsResult:
    avg:     float = 0.0
    min:     float = 0.0
    max:     float = 0.0
    low1:    float = 0.0
    p99:     float = 0.0
    samples: int = 0
    source:  str = "none"


# ── worker ─────────────────────────────────────────────────────────────────────
_POLL_MS = 100   # poll every 100ms = 10 readings/sec


def _rtss_worker(stop: threading.Event):
    buf_ptr = _open_rtss_shm()
    if not buf_ptr:
        # RTSS not available — fall back to psutil
        _psutil_worker(stop)
        return

    while not stop.is_set():
        fps = _read_valo_fps(buf_ptr)
        if fps and 1 <= fps <= 1500:
            with _lock:
                _buf.append(fps)
        time.sleep(_POLL_MS / 1000.0)

    try:
        ctypes.windll.kernel32.UnmapViewOfFile(buf_ptr)
    except Exception:
        pass


def _psutil_worker(stop: threading.Event):
    global _source
    _source = "psutil"

    proc = None
    for p in psutil.process_iter(["name", "pid"]):
        try:
            if p.info["name"] == _VALO_EXE:
                proc = p
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if not proc:
        return

    try:
        prev_sw = proc.num_ctx_switches().involuntary
        prev_t = time.perf_counter()
    except Exception:
        return

    while not stop.is_set():
        time.sleep(0.25)
        try:
            cur_sw = proc.num_ctx_switches().involuntary
            cur_t = time.perf_counter()
            dt = cur_t - prev_t
            dsw = cur_sw - prev_sw
            if dt > 0 and dsw > 0:
                fps = round(dsw / dt, 1)
                if 1 <= fps <= 1500:
                    with _lock:
                        _buf.append(fps)
            prev_sw, prev_t = cur_sw, cur_t
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break


# ── public API ─────────────────────────────────────────────────────────────────
def start_capture():
    global _capturing, _stop_evt, _thread, _buf, _source
    if _capturing:
        return

    with _lock:
        _buf = deque(maxlen=100_000)

    _source = "rtss" if is_rtss_running() else "psutil"
    _stop_evt = threading.Event()
    _thread = threading.Thread(
        target=_rtss_worker, args=(_stop_evt,), daemon=True)
    _capturing = True
    _thread.start()


def stop_capture() -> FpsResult:
    global _capturing

    if not _capturing:
        return FpsResult()

    if _stop_evt:
        _stop_evt.set()
    if _thread:
        _thread.join(timeout=5)
    _capturing = False

    with _lock:
        data = list(_buf)

    if len(data) < 3:
        return FpsResult(source="no_data")

    s = sorted(data)
    cut = max(1, int(len(s) * 0.01))
    p99_idx = max(0, int(len(s) * 0.99) - 1)

    return FpsResult(
        avg=round(statistics.mean(data), 1),
        min=round(s[0],                  1),
        max=round(s[-1],                 1),
        low1=round(statistics.mean(s[:cut]), 1),
        p99=round(s[p99_idx],            1),
        samples=len(data),
        source=_source,
    )


def get_live_fps() -> Optional[float]:
    with _lock:
        return _buf[-1] if _buf else None
