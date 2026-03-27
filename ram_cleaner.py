import ctypes
import ctypes.wintypes as wt
import psutil
import time
import subprocess
import session_logger


# ── Windows kernel constants ───────────────────────────────────────────────────
_SystemMemoryListInformation = 80

# MemoryPurgeStandbyList variants
_MemoryEmptyWorkingSets = 2
_MemoryFlushModifiedList = 3
_MemoryPurgeStandbyList = 4
_MemoryCombinePhysicalMemory = 5
_MemoryPurgeLowPriorityStandbyList = 6

# Background processes safe to terminate before gaming
_BLOAT_PROCESSES = [
    "SearchIndexer.exe",
    "OneDrive.exe",
    "Teams.exe",
    "Slack.exe",
    "Discord.exe",
    "Spotify.exe",
    "MsMpEng.exe",
    "SgrmBroker.exe",
    "WmiPrvSE.exe",
]

# These must never be killed
_PROTECTED = {
    "System", "svchost.exe", "lsass.exe", "csrss.exe",
    "winlogon.exe", "explorer.exe", "python.exe", "VALOPT.exe",
    "VALORANT-Win64-Shipping.exe", "VALORANT.exe",
}


# ── helpers ────────────────────────────────────────────────────────────────────
def _get_free_mb() -> float:
    return psutil.virtual_memory().available / 1_048_576


def _set_system_info(command: int) -> bool:
    try:
        cmd = ctypes.c_int(command)
        status = ctypes.windll.ntdll.NtSetSystemInformation(
            _SystemMemoryListInformation,
            ctypes.byref(cmd),
            ctypes.sizeof(cmd)
        )
        return status == 0   # STATUS_SUCCESS
    except Exception:
        return False


def _empty_all_working_sets() -> bool:
    try:
        # EmptyWorkingSet(-1) trims the current process
        ctypes.windll.psapi.EmptyWorkingSet(wt.HANDLE(-1))

        # Also trim every other process we can access
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"] in _PROTECTED:
                continue
            try:
                h = ctypes.windll.kernel32.OpenProcess(
                    0x1F0FFF,  # PROCESS_ALL_ACCESS
                    False,
                    proc.info["pid"]
                )
                if h:
                    ctypes.windll.psapi.EmptyWorkingSet(h)
                    ctypes.windll.kernel32.CloseHandle(h)
            except Exception:
                pass
        return True
    except Exception:
        return False


def _is_valorant_running() -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            if "valorant" in p.info["name"].lower():
                return True
        except Exception:
            pass
    return False


# ── public API ─────────────────────────────────────────────────────────────────
def clean_memory(kill_background: bool = False) -> dict:
    steps = []
    before = _get_free_mb()

    # 1. Empty all process working sets
    ok = _empty_all_working_sets()
    steps.append(("Working sets cleared", ok))

    # small delay — let OS process the trims
    time.sleep(0.3)

    # 2. Flush modified page list → moves dirty pages to standby
    ok = _set_system_info(_MemoryFlushModifiedList)
    steps.append(("Modified page list flushed", ok))

    # 3. Purge standby list → releases standby pages back to free pool
    ok = _set_system_info(_MemoryPurgeStandbyList)
    steps.append(("Standby list purged", ok))

    # 4. Purge low-priority standby list (extra pass)
    ok = _set_system_info(_MemoryPurgeLowPriorityStandbyList)
    steps.append(("Low-priority standby purged", ok))

    # 5. Combine physical memory pages (reduces duplication)
    ok = _set_system_info(_MemoryCombinePhysicalMemory)
    steps.append(("Physical memory combined", ok))

    time.sleep(0.2)

    # 6. Optional: kill background bloat (only when game not running)
    if kill_background and not _is_valorant_running():
        killed = []
        for proc in psutil.process_iter(["name", "pid"]):
            try:
                name = proc.info["name"]
                if name in _BLOAT_PROCESSES and name not in _PROTECTED:
                    proc.kill()
                    killed.append(name)
            except Exception:
                pass
        if killed:
            steps.append(
                (f"Killed background apps: {', '.join(killed)}", True))

    after = _get_free_mb()
    freed = max(0.0, after - before)
    success = freed > 0 or any(ok for _, ok in steps)

    # log to session_logger
    session_logger.add_log(
        f"RAM Clean: freed ~{freed:.0f} MB  "
        f"({before:.0f} MB → {after:.0f} MB free)",
        "SUCCESS" if success else "FAILED"
    )

    return {
        "freed_mb":  round(freed,  1),
        "before_mb": round(before, 1),
        "after_mb":  round(after,  1),
        "steps":     steps,
        "success":   success,
    }
