import os
import json
import time
from dataclasses import dataclass, asdict, field
from typing import Optional, List


_DATA_DIR = os.path.join(os.getenv("LOCALAPPDATA", ""), "VALOPT")
_DATA_FILE = os.path.join(_DATA_DIR, "benchmark.json")
os.makedirs(_DATA_DIR, exist_ok=True)


@dataclass
class FpsSnapshot:
    avg:     float = 0.0
    min:     float = 0.0
    max:     float = 0.0
    low1:    float = 0.0
    samples: int = 0
    source:  str = ""
    ts:      str = ""


@dataclass
class BenchmarkRecord:
    before:  Optional[FpsSnapshot] = None
    after:   Optional[FpsSnapshot] = None
    changes: List[str] = field(default_factory=list)


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _snap(fps) -> FpsSnapshot:
    return FpsSnapshot(
        avg=fps.avg, min=fps.min, max=fps.max,
        low1=fps.low1, samples=fps.samples, source=fps.source, ts=_now()
    )


def _load_raw() -> dict:
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_raw(data: dict):
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _log(msg: str, status: str = "SUCCESS"):
    try:
        import session_logger
        session_logger.add_log(msg, status)
    except Exception:
        pass


# ── Public API ─────────────────────────────────────────────────────────────────
def save_before(fps_result):
    data = _load_raw()
    data["before"] = asdict(_snap(fps_result))
    data["after"] = None
    data["changes"] = []
    _save_raw(data)
    _log(
        f"Benchmark BEFORE: avg={fps_result.avg} min={fps_result.min} "
        f"max={fps_result.max} 1%low={fps_result.low1} src={fps_result.source}",
        "SUCCESS"
    )


def save_after(fps_result, changes: List[str]):
    data = _load_raw()
    data["after"] = asdict(_snap(fps_result))
    data["changes"] = changes
    _save_raw(data)
    _log(
        f"Benchmark AFTER: avg={fps_result.avg} min={fps_result.min} "
        f"max={fps_result.max} 1%low={fps_result.low1} src={fps_result.source}",
        "SUCCESS"
    )
    for c in changes:
        _log(f"  Applied change: {c}", "SUCCESS")


def load() -> Optional[BenchmarkRecord]:
    data = _load_raw()
    if not data:
        return None

    def to_snap(d) -> Optional[FpsSnapshot]:
        return FpsSnapshot(**d) if d else None

    return BenchmarkRecord(
        before=to_snap(data.get("before")),
        after=to_snap(data.get("after")),
        changes=data.get("changes", []),
    )


def clear():
    _save_raw({})
    _log("Benchmark data cleared", "SUCCESS")
