import os
import re
import glob
import json
import time
import threading
import statistics
import psutil
from collections import deque
from dataclasses import dataclass
from typing import Optional

_PROCESS_NAME = "VALORANT-Win64-Shipping.exe"

_VALO_LOG = os.path.join(
    os.getenv("LOCALAPPDATA", ""),
    "VALORANT", "Saved", "Logs", "ShooterGame.log"
)

_CFX_DIR = os.path.join(
    os.path.expanduser("~"), "Documents", "CapFrameX", "Captures"
)

_RE_FPS = re.compile(r"FPS[:\s]+([\d.]+)")
_RE_FRAMETIME = re.compile(r"FrameTime[:\s]+([\d.]+)\s*ms", re.IGNORECASE)


@dataclass
class FpsResult:
    avg:     float = 0.0
    min:     float = 0.0
    max:     float = 0.0
    low1:    float = 0.0
    samples: int = 0
    source:  str = "none"


def is_valorant_running() -> bool:
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] == _PROCESS_NAME:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def detect_source() -> str:
    if os.path.exists(_VALO_LOG):
        return "log"
    if os.path.isdir(_CFX_DIR) and glob.glob(os.path.join(_CFX_DIR, "*.json")):
        return "capframex"
    if is_valorant_running():
        return "psutil"
    return "none"


def _fps_from_cfx_json(path: str) -> list:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        fps_values = []
        runs = data.get("Runs", [data])
        for run in runs:
            cap = run.get("CaptureData", run)
            frametimes = (
                cap.get("MsBetweenPresents") or
                cap.get("MsBetweenDisplayChange") or
                []
            )
            for ft in frametimes:
                try:
                    ft_f = float(ft)
                    if 0.5 < ft_f < 200:    # valid range: 5 – 2000 fps
                        fps_values.append(round(1000.0 / ft_f, 2))
                except (TypeError, ValueError, ZeroDivisionError):
                    pass
        return fps_values
    except Exception:
        return []


_samples:    deque = deque(maxlen=10_000)
_capturing:  bool = False
_stop_event: Optional[threading.Event] = None
_thread:     Optional[threading.Thread] = None
_lock:       threading.Lock = threading.Lock()
_active_src: str = "none"


def _log_tail_worker(buf: deque, stop: threading.Event):
    if not os.path.exists(_VALO_LOG):
        return
    try:
        with open(_VALO_LOG, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, 2)
            while not stop.is_set():
                line = f.readline()
                if not line:
                    time.sleep(0.04)
                    continue
                m = _RE_FPS.search(line)
                if m:
                    buf.append(float(m.group(1)))
                    continue
                m = _RE_FRAMETIME.search(line)
                if m:
                    ms = float(m.group(1))
                    if ms > 0:
                        buf.append(round(1000.0 / ms, 2))
    except Exception:
        pass


def _cfx_watcher(buf: deque, stop: threading.Event):
    start_time = time.time()
    seen: set = set()

    for f in glob.glob(os.path.join(_CFX_DIR, "*.json")):
        seen.add(f)

    while not stop.is_set():
        time.sleep(2)
        try:
            for f in glob.glob(os.path.join(_CFX_DIR, "*.json")):
                if f in seen:
                    continue
                fps_list = _fps_from_cfx_json(f)
                if fps_list:
                    buf.extend(fps_list)
                seen.add(f)
        except Exception:
            pass


def _psutil_worker(buf: deque, stop: threading.Event):
    proc = None
    for p in psutil.process_iter(["name", "pid"]):
        try:
            if p.info["name"] == _PROCESS_NAME:
                proc = p
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if proc is None:
        return

    prev_cpu = proc.cpu_times().user
    prev_t = time.perf_counter()

    while not stop.is_set():
        time.sleep(0.5)
        try:
            cur_cpu = proc.cpu_times().user
            cur_t = time.perf_counter()
            dt, dc = cur_t - prev_t, cur_cpu - prev_cpu
            if dt > 0 and dc > 0:
                fps_est = max(1.0, min((dc / dt) * 60, 500.0))
                buf.append(round(fps_est, 1))
            prev_cpu, prev_t = cur_cpu, cur_t
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break


def _capture_worker(stop: threading.Event, source: str):
    global _samples
    with _lock:
        _samples = deque(maxlen=10_000)

    workers = []

    if source == "log":
        workers.append(threading.Thread(
            target=_log_tail_worker, args=(_samples, stop), daemon=True))
        if os.path.isdir(_CFX_DIR):
            workers.append(threading.Thread(
                target=_cfx_watcher, args=(_samples, stop), daemon=True))

    elif source == "capframex":
        workers.append(threading.Thread(
            target=_cfx_watcher, args=(_samples, stop), daemon=True))
        workers.append(threading.Thread(
            target=_psutil_worker, args=(_samples, stop), daemon=True))

    else:
        workers.append(threading.Thread(
            target=_psutil_worker, args=(_samples, stop), daemon=True))

    for w in workers:
        w.start()
    stop.wait()
    for w in workers:
        w.join(timeout=2)


def start_capture():
    global _capturing, _thread, _stop_event, _active_src
    if _capturing:
        return
    _active_src = detect_source()
    _stop_event = threading.Event()
    _thread = threading.Thread(
        target=_capture_worker, args=(_stop_event, _active_src), daemon=True)
    _capturing = True
    _thread.start()


def stop_capture() -> FpsResult:
    global _capturing
    if not _capturing or _stop_event is None:
        return FpsResult()

    _stop_event.set()
    if _thread:
        _thread.join(timeout=3)
    _capturing = False

    with _lock:
        data = list(_samples)

    if not data:
        return FpsResult(source="no_data")

    data_sorted = sorted(data)
    cut = max(1, int(len(data_sorted) * 0.01))
    low1 = statistics.mean(data_sorted[:cut])

    return FpsResult(
        avg=round(statistics.mean(data), 1),
        min=round(min(data),             1),
        max=round(max(data),             1),
        low1=round(low1,                  1),
        samples=len(data),
        source=_active_src,
    )


def get_live_fps() -> Optional[float]:
    with _lock:
        return _samples[-1] if _samples else None


def parse_capframex_file(path: str) -> Optional[FpsResult]:
    data = _fps_from_cfx_json(path)
    if not data:
        return None
    data_sorted = sorted(data)
    cut = max(1, int(len(data_sorted) * 0.01))
    return FpsResult(
        avg=round(statistics.mean(data), 1),
        min=round(min(data),             1),
        max=round(max(data),             1),
        low1=round(statistics.mean(data_sorted[:cut]), 1),
        samples=len(data),
        source="capframex",
    )
