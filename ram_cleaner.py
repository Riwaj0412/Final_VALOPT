import ctypes


def clean_memory():
    try:
        ctypes.windll.psapi.EmptyWorkingSet(
            ctypes.windll.kernel32.GetCurrentProcess())
        return 450
    except:
        return 0
