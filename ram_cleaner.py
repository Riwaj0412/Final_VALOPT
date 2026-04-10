import ctypes
import ctypes.wintypes as wt
import psutil
import time
import session_logger


# Windows constants
_SysMemListInfo = 80
_FlushModifiedList = 3
_PurgeStandbyList = 4
_PurgeLowPriority = 6
_CombinePhysical = 5


def _free_mb() -> float:
    return psutil.virtual_memory().available / 1_048_576


def _set_sys_info(command: int) -> bool:
    try:
        cmd = ctypes.c_int(command)
        status = ctypes.windll.ntdll.NtSetSystemInformation(
            _SysMemListInfo, ctypes.byref(cmd), ctypes.sizeof(cmd))
        return status == 0
    except Exception:
        return False


def _empty_working_sets() -> bool:
    try:
        # Current process
        ctypes.windll.psapi.EmptyWorkingSet(wt.HANDLE(-1))

        # All other processes
        for proc in psutil.process_iter(["pid", "name"]):
            safe = {"System", "lsass.exe", "csrss.exe", "winlogon.exe"}
            if proc.info["name"] in safe:
                continue
            try:
                h = ctypes.windll.kernel32.OpenProcess(
                    0x1F0FFF, False, proc.info["pid"])
                if h:
                    ctypes.windll.psapi.EmptyWorkingSet(h)
                    ctypes.windll.kernel32.CloseHandle(h)
            except Exception:
                pass
        return True
    except Exception:
        return False


def clean_memory() -> dict:
    before = _free_mb()

    _empty_working_sets()
    time.sleep(0.2)
    _set_sys_info(_FlushModifiedList)
    _set_sys_info(_PurgeStandbyList)
    _set_sys_info(_PurgeLowPriority)
    _set_sys_info(_CombinePhysical)
    time.sleep(0.3)

    after = _free_mb()
    freed = max(0.0, after - before)

    session_logger.add_log(
        f"RAM Clean: {freed:.0f} MB freed ({before:.0f} → {after:.0f} MB free)",
        "SUCCESS" if freed > 0 else "OK"
    )

    return {
        "freed_mb":  round(freed,  1),
        "before_mb": round(before, 1),
        "after_mb":  round(after,  1),
        "success":   True,
    }
