import os
import sys
import ctypes
import winreg
import subprocess
import platform
import psutil

# Windows API structures for display settings


class DEVMODE(ctypes.Structure):
    _fields_ = [("dmDeviceName", ctypes.c_wchar * 32),
                ("dmSpecVersion", ctypes.c_ushort),
                ("dmDriverVersion", ctypes.c_ushort),
                ("dmSize", ctypes.c_ushort),
                ("dmDriverExtra", ctypes.c_ushort),
                ("dmFields", ctypes.c_uint),
                ("dmOrientation", ctypes.c_short),
                ("dmPaperSize", ctypes.c_short),
                ("dmPaperLength", ctypes.c_short),
                ("dmPaperWidth", ctypes.c_short),
                ("dmScale", ctypes.c_short),
                ("dmCopies", ctypes.c_short),
                ("dmDefaultSource", ctypes.c_short),
                ("dmPrintQuality", ctypes.c_short),
                ("dmColor", ctypes.c_short),
                ("dmDuplex", ctypes.c_short),
                ("dmYResolution", ctypes.c_short),
                ("dmTTOption", ctypes.c_short),
                ("dmCollate", ctypes.c_short),
                ("dmFormName", ctypes.c_wchar * 32),
                ("dmLogPixels", ctypes.c_ushort),
                ("dmBitsPerPel", ctypes.c_uint),
                ("dmPelsWidth", ctypes.c_uint),
                ("dmPelsHeight", ctypes.c_uint),
                ("dmDisplayFlags", ctypes.c_uint),
                ("dmDisplayFrequency", ctypes.c_uint),
                ("unused3", ctypes.c_byte * 10)]


def get_registry_value(path, name):
    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


def get_clean_cpu_name():
    """Queries the Windows Registry for the precise marketing name of the CPU."""
    try:
        path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        cpu_name, _ = winreg.QueryValueEx(reg_key, "ProcessorNameString")
        winreg.CloseKey(reg_key)

        # Remove TM/R symbols and extra whitespace for a cleaner UI
        return cpu_name.replace("(TM)", "").replace("(R)", "").strip()
    except Exception:
        # Fallback if registry access is restricted
        return platform.processor() or "Unknown Processor"


def get_exact_gpu_name():
    gpu_names = []
    try:
        path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
            for i in range(10):
                try:
                    with winreg.OpenKey(key, f"{i:04d}") as subkey:
                        driver_desc = winreg.QueryValueEx(
                            subkey, "DriverDesc")[0]
                        if not any(x in driver_desc for x in ["Microsoft", "Citrix", "Remote", "Basic"]):
                            gpu_names.append(driver_desc)
                except:
                    continue
        return gpu_names[0] if gpu_names else "Standard Graphics Adapter"
    except:
        return "NVIDIA GeForce RTX Series"


def get_supported_resolutions():
    """Fetches all valid resolutions supported by the primary monitor."""
    resolutions = set()
    dm = DEVMODE()
    i = 0
    while ctypes.windll.user32.EnumDisplaySettingsW(None, i, ctypes.byref(dm)):
        if dm.dmPelsWidth >= 800:
            resolutions.add(f"{dm.dmPelsWidth}x{dm.dmPelsHeight}")
        i += 1
    return sorted(list(resolutions), key=lambda x: int(x.split('x')[0]), reverse=True)


def get_supported_refresh_rates():
    """Fetches all valid refresh rates supported by the primary monitor."""
    rates = set()
    dm = DEVMODE()
    i = 0
    while ctypes.windll.user32.EnumDisplaySettingsW(None, i, ctypes.byref(dm)):
        if dm.dmDisplayFrequency > 1:
            rates.add(f"{dm.dmDisplayFrequency}Hz")
        i += 1
    return sorted(list(rates), key=lambda x: int(x.replace('Hz', '')), reverse=True)


def get_monitor_specs():
    try:
        dm = DEVMODE()
        ctypes.windll.user32.EnumDisplaySettingsW(None, -1, ctypes.byref(dm))
        width = dm.dmPelsWidth
        height = dm.dmPelsHeight
        hz = dm.dmDisplayFrequency
        return f"{width}x{height} @ {hz}Hz"
    except:
        return "1920x1080 @ 60Hz"


def check_valorant_presence():
    for drive in ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
        path = f"{drive}:\\Riot Games\\VALORANT\\live"
        if os.path.exists(path):
            return True
    return False


def get_system_report():
    """Compiles all gathered hardware information into a clean dictionary."""
    return {
        'cpu': get_clean_cpu_name(),
        'ram': f"{round(psutil.virtual_memory().total / (1024**3))} GB DDR4/DDR5",
        'gpu': get_exact_gpu_name(),
        'os': f"Windows {platform.release()}",
        'display': get_monitor_specs(),
        'valorant_installed': check_valorant_presence()
    }


if __name__ == "__main__":
    # Test the output
    report = get_system_report()
    print("--- System Report ---")
    for key, value in report.items():
        print(f"{key.upper()}: {value}")
