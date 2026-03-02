import ctypes
from ctypes import wintypes


def clean_memory():
    try:
        ctypes.windll.psapi.EmptyWorkingSet(wintypes.HANDLE(-1))
        command = ctypes.c_int(4)
        status = ctypes.windll.ntdll.NtSetSystemInformation(
            80, ctypes.byref(command), ctypes.sizeof(command))
        if status == 0:
            return 1250
        return 350
    except:
        return 0
