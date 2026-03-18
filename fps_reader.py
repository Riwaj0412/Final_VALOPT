import os
import re
import csv
import glob
import json
import time
import shutil
import subprocess
import threading
import statistics
import psutil
from collections import deque
from dataclasses import dataclass
from typing import Optional


_VALO_EXE = "VALORANT-Win64-Shipping.exe"
_PM_EXE_NAME = "PresentMon64.exe"

_CFX_DIR = os.path.join(
    os.path.expanduser("~"), "Documents", "CapFrameX", "Captures"
)

_COL_MS_BETWEEN = "msBetweenPresents"
_COL_DISPLAYED = "msUntilDisplayed"


@dataclass
class FpsResult:
    avg:     float = 0.0
    min:     float = 0.0
    max:     float = 0.0
    low1:    float = 0.0
    samples: int = 0
    source:  str = "none"


def is_valorant_running() -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] == _VALO_EXE:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def find_presentmon() -> Optional[str]:
    candidates = [
        os.path.join(os.path.dirname(__file__), _PM_EXE_NAME),
        os.path.join(os.path.dirname(__file__), "PresentMon64a.exe"),
        os.path.join(os.path.dirname(__file__), "tools", _PM_EXE_NAME),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    # Try PATH
    found = shutil.which(_PM_EXE_NAME) or shutil.which("PresentMon64a.exe")
    return found


def detect_source() -> str:
    if find_presentmon():
        return "presentmon"
    if os.path.isdir(_CFX_DIR) and glob.glob(os.path.join(_CFX_DIR, "*.json")):
        return "capframex"
    if is_valorant_running():
        return "psutil"
    return "none"


_samples:    deque = deque(maxlen=50_000)
_capturing:  bool = False
_stop_event: Optional[threading.Event] = None
_thread:     Optional[threading.Thread] = None
_lock:       threading.Lock = threading.Lock()
_active_src: str = "none"
_pm_proc:    Optional[subprocess.Popen] = None


def _presentmon_worker(buf: deque, stop: threading.Event, pm_path: str):
    global _pm_proc

    cmd = [
        pm_path,
        "--process_name", _VALO_EXE,
        "--output_stdout",
        "--stop_existing_session",
    ]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            creationflags=0x08000000
        )
        _pm_proc = proc
    except Exception:
        _pm_proc = None
        return

    col_idx = None
    header_found = False

    try:
        for raw_line in proc.stdout:
            if stop.is_set():
                break

            line = raw_line.strip()
            if not line:
                continue

            # First non-empty line is the CSV header
            if not header_found:
                cols = [c.strip() for c in line.split(",")]
                # Try primary column, then fallback
                if _COL_MS_BETWEEN in cols:
                    col_idx = cols.index(_COL_MS_BETWEEN)
                elif _COL_DISPLAYED in cols:
                    col_idx = cols.index(_COL_DISPLAYED)
                header_found = True
                continue

            if col_idx is None:
                continue

            parts = line.split(",")
            if len(parts) <= col_idx:
                continue

            try:
                ms = float(parts[col_idx])
                if 0.3 < ms < 500:          # valid range ~ 2 – 3000 fps
                    buf.append(round(1000.0 / ms, 1))
            except (ValueError, ZeroDivisionError):
                pass

    except Exception:
        pass
    finally:
        try:
            proc.terminate()
        except Exception:
            pass
        _pm_proc = None


def _fps_from_cfx_json(path: str) -> list:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        fps_values = []
        runs = data.get("Runs", [data])
        for run in runs:
            cap = run.get("CaptureData", run)
            frametimes = (cap.get("MsBetweenPresents") or
                          cap.get("MsBetweenDisplayChange") or [])
            for ft in frametimes:
                try:
                    ft_f = float(ft)
                    if 0.3 < ft_f < 500:
                        fps_values.append(round(1000.0 / ft_f, 1))
                except (TypeError, ValueError, ZeroDivisionError):
                    pass
        return fps_values
    except Exception:
        return []


def _cfx_watcher(buf: deque, stop: threading.Event):
    seen: set = set(glob.glob(os.path.join(_CFX_DIR, "*.json")))
    while not stop.is_set():
        time.sleep(2)
        try:
            for f in glob.glob(os.path.join(_CFX_DIR, "*.json")):
                if f not in seen:
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
            if p.info["name"] == _VALO_EXE:
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
                fps_est = max(1.0, min((dc / dt) * 60, 1000.0))
                buf.append(round(fps_est, 1))
            prev_cpu, prev_t = cur_cpu, cur_t
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break


def _capture_worker(stop: threading.Event, source: str):
    global _samples
    with _lock:
        _samples = deque(maxlen=50_000)

    workers = []

    if source == "presentmon":
        pm = find_presentmon()
        if pm:
            workers.append(threading.Thread(
                target=_presentmon_worker, args=(_samples, stop, pm), daemon=True))
        else:
            source = "psutil"

    if source == "capframex":
        workers.append(threading.Thread(
            target=_cfx_watcher, args=(_samples, stop), daemon=True))
        workers.append(threading.Thread(
            target=_psutil_worker, args=(_samples, stop), daemon=True))

    if source == "psutil":
        workers.append(threading.Thread(
            target=_psutil_worker, args=(_samples, stop), daemon=True))

    for w in workers:
        w.start()
    stop.wait()
    for w in workers:
        w.join(timeout=3)


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
    global _capturing, _pm_proc

    if not _capturing or _stop_event is None:
        return FpsResult()

    if _pm_proc:
        try:
            _pm_proc.terminate()
        except Exception:
            pass

    _stop_event.set()
    if _thread:
        _thread.join(timeout=5)
    _capturing = False

    with _lock:
        data = list(_samples)

    if not data:
        return FpsResult(source="no_data")

    data_sorted = sorted(data)
    cut = max(1, int(len(data_sorted) * 0.01))

    return FpsResult(
        avg=round(statistics.mean(data), 1),
        min=round(min(data),             1),
        max=round(max(data),             1),
        low1=round(statistics.mean(data_sorted[:cut]), 1),
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
