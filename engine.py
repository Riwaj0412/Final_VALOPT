import os
import sys
import ctypes
import winreg

def get_registry_value(path, name):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

def get_exact_gpu_name():
    """Scans the Windows Registry for all installed display drivers to find the dedicated GPU."""
    gpu_names = []
    try:
        # The specific class ID for Display Adapters in the Windows Registry
        path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
            # Check the first 10 registry subkeys (0000, 0001, etc.)
            for i in range(10):
                try:
                    with winreg.OpenKey(key, f"{i:04d}") as subkey:
                        driver_desc = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                        # Filter out basic software or remote drivers
                        if not any(x in driver_desc for x in ["Microsoft", "Citrix", "Remote"]):
                            gpu_names.append(driver_desc)
                except:
                    continue
        
        if gpu_names:
            # Priority: Look for NVIDIA/AMD/RTX/ARC gaming cards first
            dedicated = [g for g in gpu_names if any(x in g.upper() for x in ["NVIDIA", "RTX", "GTX", "RADEON", "ARC"])]
            return dedicated[0] if dedicated else gpu_names[0]
            
    except Exception:
        pass
    return "Integrated Graphics or Unindentified"

def get_system_report():
    report = {
        "cpu": "Unknown Processor",
        "gpu": "Unknown Graphics",
        "ram": "0 GB",
        "os": "Windows"
    }

    # 1. CPU - Direct from Registry
    cpu = get_registry_value(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "ProcessorNameString")
    if cpu: 
        report["cpu"] = cpu.strip()

    # 2. RAM - Direct Kernel Access
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_uint), ("dwMemoryLoad", ctypes.c_uint),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(stat)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        report["ram"] = f"{round(stat.ullTotalPhys / (1024**3))} GB"
    except:
        report["ram"] = "16 GB"

    # 3. GPU - Using Deep Registry Scan
    report["gpu"] = get_exact_gpu_name()

    # 4. OS Build
    try:
        build = sys.getwindowsversion().build
        report["os"] = "Windows 11" if build >= 22000 else "Windows 10"
    except:
        report["os"] = "Windows"

    return report

def get_monitor_specs():
    try:
        # 1. Force DPI Awareness
        ctypes.windll.user32.SetProcessDPIAware()
        width = ctypes.windll.user32.GetSystemMetrics(0)
        height = ctypes.windll.user32.GetSystemMetrics(1)

        # 2. Try the primary method (User32 Enum)
        class DEVMODE(ctypes.Structure):
            _fields_ = [("dmDeviceName", ctypes.c_char * 32), ("unused", ctypes.c_byte * 88),
                        ("dmFields", ctypes.c_uint), ("unused2", ctypes.c_byte * 44),
                        ("dmDisplayFrequency", ctypes.c_uint), ("unused3", ctypes.c_byte * 10)]
        
        dm = DEVMODE()
        ctypes.windll.user32.EnumDisplaySettingsW(None, -1, ctypes.byref(dm))
        hz = dm.dmDisplayFrequency

        if hz <= 32:
            cmd = "powershell -command \"(Get-CimInstance Win32_VideoController).CurrentRefreshRate\""
            shell_out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
            # If multiple controllers (Intel + NVIDIA), take the highest value found
            rates = [int(s) for s in shell_out.split() if s.isdigit()]
            if rates:
                hz = max(rates)

        # 4. Final safety fallback
        if hz <= 32: hz = 60 

        return f"{width}x{height} @ {hz}Hz"
    except:
        return "1920x1080 @ 60Hz"

def check_valorant_presence():
    # Check C, D, and E drives for the live game folder
    for drive in ['C', 'D', 'E','F', 'G', 'H']:
        path = f"{drive}:\\Riot Games\\VALORANT\\live"
        if os.path.exists(path):
            return True
    return False

# --- Test Output ---
if __name__ == "__main__":
    print("--- FETCHING SYSTEM SPECS ---")
    specs = get_system_report()
    mon = get_monitor_specs()
    
    print(f"OS:      {specs['os']}")
    print(f"CPU:     {specs['cpu']}")
    print(f"GPU:     {specs['gpu']}")
    print(f"RAM:     {specs['ram']}")
    print(f"MONITOR: {mon}")
    print(f"VALO:    {'Detected' if check_valorant_presence() else 'Not Found'}")