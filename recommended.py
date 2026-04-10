import subprocess
import ctypes
import os
import glob
import session_logger

from extreme_fps import apply_extreme_optimizations
from ram_cleaner import clean_memory
from power_plan import set_max_power


def _is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def _apply_power_plan(results):
    ok = set_max_power()
    results.append(("Power Plan → High Performance", ok))
    session_logger.add_log(
        "Recommended: Power Plan applied" if ok
        else "Recommended: Power Plan FAILED", "OK" if ok else "FAILED"
    )


def _apply_extreme_fps(results):
    ok, msg = apply_extreme_optimizations()
    results.append((f"Extreme FPS → {msg}", ok))
    session_logger.add_log(
        f"Recommended: Extreme FPS — {msg}", "OK" if ok else "FAILED"
    )


def _clean_ram(results):
    result = clean_memory()
    # clean_memory() returns a dict: {freed_mb, before_mb, after_mb, success}
    if isinstance(result, dict):
        freed = result.get("freed_mb", 0)
        ok = result.get("success", False)
    else:
        # fallback if old version returns int
        freed = result if isinstance(result, (int, float)) else 0
        ok = freed > 0
    label = f"RAM Cleaned → ~{freed:.0f} MB freed" if ok else "RAM Clean skipped"
    results.append((label, ok))
    session_logger.add_log(
        f"Recommended: {label}", "OK" if ok else "WARN"
    )


def _disable_game_dvr(results):
    if not _is_admin():
        results.append(("Game DVR disable → skipped (no admin)", False))
        session_logger.add_log(
            "Recommended: Game DVR skipped — not admin", "WARN")
        return

    tweaks = [
        # Disable Game DVR
        (r"HKCU\System\GameConfigStore", "GameDVR_Enabled", "REG_DWORD", "0"),
        # Disable Game Bar
        (r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR",
         "AppCaptureEnabled", "REG_DWORD", "0"),
    ]

    all_ok = True
    for hive_key, value_name, reg_type, data in tweaks:
        try:
            subprocess.run(
                f'reg add "{hive_key}" /v {value_name} /t {reg_type} /d {data} /f',
                shell=True, check=True,
                creationflags=0x08000000,   # CREATE_NO_WINDOW
                capture_output=True
            )
        except Exception as e:
            all_ok = False
            session_logger.add_log(
                f"Recommended: Game DVR reg error — {e}", "FAILED")

    results.append(("Game DVR / Game Bar disabled", all_ok))
    session_logger.add_log(
        "Recommended: Game DVR disabled" if all_ok
        else "Recommended: Game DVR partial failure",
        "OK" if all_ok else "WARN"
    )


def _set_valorant_high_priority(results):
    ps_script = (
        "$p = Get-Process 'VALORANT-Win64-Shipping' -ErrorAction SilentlyContinue;"
        "if ($p) { $p.PriorityClass = 'High'; exit 0 } else { exit 1 }"
    )
    try:
        result = subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
            creationflags=0x08000000,
            capture_output=True
        )
        ok = result.returncode == 0
        label = "Valorant CPU priority → High" if ok else "Valorant priority → not running (skipped)"
        results.append((label, ok))
        session_logger.add_log(f"Recommended: {label}", "OK" if ok else "WARN")
    except Exception as e:
        results.append(("Valorant CPU priority → error", False))
        session_logger.add_log(f"Recommended: Priority error — {e}", "FAILED")


def _flush_dns(results):
    try:
        subprocess.run(
            "ipconfig /flushdns", shell=True, check=True,
            creationflags=0x08000000, capture_output=True
        )
        results.append(("DNS Cache flushed", True))
        session_logger.add_log("Recommended: DNS flushed", "OK")
    except Exception as e:
        results.append(("DNS flush failed", False))
        session_logger.add_log(f"Recommended: DNS flush error — {e}", "FAILED")


def apply_recommended_optimizations():
    session_logger.add_log("Recommended: ── START ──", "OK")

    results = []

    _apply_power_plan(results)
    _apply_extreme_fps(results)
    _clean_ram(results)
    _disable_game_dvr(results)
    _set_valorant_high_priority(results)
    _flush_dns(results)

    passed = sum(1 for _, ok in results if ok)
    session_logger.add_log(
        f"Recommended: ── DONE  {passed}/{len(results)} steps OK ──", "OK"
    )

    return results
