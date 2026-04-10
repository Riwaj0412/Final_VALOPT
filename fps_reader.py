import ctypes
import ctypes.wintypes
import time
import threading
import statistics
import psutil
import subprocess
import re
from collections import deque
from dataclasses import dataclass
from typing import Optional

_VALO_EXE = "VALORANT-Win64-Shipping.exe"


@dataclass
class FpsResult:
    avg:     float = 0.0
    min:     float = 0.0
    max:     float = 0.0
    low1:    float = 0.0
    p99:     float = 0.0
    samples: int = 0
    source:  str = "none"


# ── helpers ────────────────────────────────────────────────────────────────────
def is_valorant_running() -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] == _VALO_EXE:
                return True
        except Exception:
            pass
    return False


def is_rtss_running() -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] == "RTSS.exe":
                return True
        except Exception:
            pass
    return False


def _get_valo_pid() -> Optional[int]:
    for p in psutil.process_iter(["name", "pid"]):
        try:
            if p.info["name"] == _VALO_EXE:
                return p.info["pid"]
        except Exception:
            pass
    return None


# ── Method 1: RTSS shared memory ──────────────────────────────────────────────
_RTSS_SHM = "RTSSSharedMemoryV2"
_RTSS_SIG = 0x53535452


class _RTSSHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("dwSignature",    ctypes.c_uint32),
        ("dwVersion",      ctypes.c_uint32),
        ("dwAppEntrySize", ctypes.c_uint32),
        ("dwAppArrOffset", ctypes.c_uint32),
        ("dwAppArrSize",   ctypes.c_uint32),
        ("dwOSDEntrySize", ctypes.c_uint32),
        ("dwOSDArrOffset", ctypes.c_uint32),
        ("dwOSDArrSize",   ctypes.c_uint32),
        ("dwOSDFrame",     ctypes.c_uint32),
    ]


def _rtss_get_fps() -> Optional[float]:
    try:
        FILE_MAP_READ = 0x0004
        k32 = ctypes.windll.kernel32

        h = k32.OpenFileMappingW(FILE_MAP_READ, False,
                                 ctypes.c_wchar_p(_RTSS_SHM))
        if not h:
            return None

        buf = k32.MapViewOfFile(h, FILE_MAP_READ, 0, 0, 65536)
        k32.CloseHandle(h)
        if not buf:
            return None

        try:
            hdr = _RTSSHeader.from_address(buf)
            if hdr.dwSignature != _RTSS_SIG or hdr.dwVersion < 0x00020000:
                return None

            entry_size = hdr.dwAppEntrySize
            if entry_size < 100:
                return None

            for i in range(min(hdr.dwAppArrSize, 32)):
                addr = buf + hdr.dwAppArrOffset + i * entry_size

                name_buf = (ctypes.c_char * 260).from_address(addr + 4)
                name = name_buf.value.decode("utf-8", errors="ignore").lower()

                if "valorant" not in name and "win64-shipping" not in name:
                    continue

                frame_time = ctypes.c_uint32.from_address(addr + 28).value
                if frame_time > 0:
                    fps = 1_000_000.0 / frame_time
                    if 1 <= fps <= 1500:
                        return round(fps, 1)

                for offset in [844, 848, 852, 856]:
                    try:
                        val = ctypes.c_uint32.from_address(addr + offset).value
                        if val > 0:
                            fps = val / 1000.0
                            if 1 <= fps <= 1500:
                                return round(fps, 1)
                    except Exception:
                        pass

        finally:
            k32.UnmapViewOfFile(buf)

    except Exception:
        pass
    return None


# ── Method 2: Windows GPU performance counter ──────────────────────────────────
def _gpu_counter_fps(pid: int) -> Optional[float]:
    try:
        # Query GPU Engine running time for this PID
        cmd = (
            f"(Get-Counter '\\GPU Engine(pid_{pid}*)\\Running Time').CounterSamples"
            f" | Measure-Object CookedValue -Sum | Select-Object -ExpandProperty Sum"
        )
        out = subprocess.check_output(
            ["powershell", "-WindowStyle", "Hidden", "-Command", cmd],
            stderr=subprocess.DEVNULL,
            timeout=3,
            creationflags=0x08000000
        ).decode(errors="ignore").strip()

        val = float(out)

        if val > 0:
            fps = val / 166667.0  # rough conversion
            if 1 <= fps <= 1500:
                return round(fps, 1)
    except Exception:
        pass
    return None


# ── Method 3: Process frame counter (psutil) ───────────────────────────────────
_SAMPLE_INTERVAL = 0.2   # seconds — sample every 200ms


def _psutil_worker(buf: deque, stop: threading.Event):
    proc = None
    for p in psutil.process_iter(["name", "pid"]):
        try:
            if p.info["name"] == _VALO_EXE:
                proc = psutil.Process(p.info["pid"])
                break
        except Exception:
            pass
    if not proc:
        return

    try:
        prev_sw = proc.num_ctx_switches().involuntary
        prev_t = time.perf_counter()
    except Exception:
        return

    while not stop.is_set():
        time.sleep(_SAMPLE_INTERVAL)
        try:
            cur_sw = proc.num_ctx_switches().involuntary
            cur_t = time.perf_counter()
            dt = cur_t - prev_t
            dsw = cur_sw - prev_sw

            if dt > 0 and dsw > 0:
                fps = round(dsw / dt, 1)
                if 1 <= fps <= 1500:
                    buf.append(fps)

            prev_sw, prev_t = cur_sw, cur_t
        except Exception:
            break


# ── RTSS polling worker ────────────────────────────────────────────────────────
def _rtss_worker(buf: deque, stop: threading.Event):
    """Poll RTSS shared memory every 100ms."""
    while not stop.is_set():
        fps = _rtss_get_fps()
        if fps:
            buf.append(fps)
        time.sleep(0.1)


# ── Capture state ──────────────────────────────────────────────────────────────
_buf:       deque = deque(maxlen=100_000)
_capturing: bool = False
_stop_evt:  Optional[threading.Event] = None
_thread:    Optional[threading.Thread] = None
_lock:      threading.Lock = threading.Lock()
_source:    str = "none"


def start_capture():
    global _capturing, _stop_evt, _thread, _buf, _source
    if _capturing:
        return

    with _lock:
        _buf = deque(maxlen=100_000)

    _stop_evt = threading.Event()

    # Pick best available method
    if is_rtss_running():
        _source = "rtss"
        worker = _rtss_worker
    else:
        _source = "psutil"
        worker = _psutil_worker

    _thread = threading.Thread(
        target=worker, args=(_buf, _stop_evt), daemon=True)
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

    if len(data) < 5:
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
