import psutil
import winreg
import os
import ctypes


def set_cpu_high():
    target = "VALORANT-Win64-Shipping.exe"
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == target:
                proc.nice(psutil.HIGH_PRIORITY_CLASS)
                return True, "CPU Priority: HIGH (Valorant)"
        return False, "Valorant is not running! Open the game first."
    except psutil.AccessDenied:
        return False, "Access Denied: Run VALOPT as Admin."
    except Exception as e:
        return False, f"Error: {str(e)}"


def set_gpu_high():
    path = r"Software\Microsoft\DirectX\UserGpuPreferences"
    # Note: This path is the default; users may need to verify their install location
    val_path = r"C:\Riot Games\VALORANT\live\ShooterGame\Binaries\Win64\VALORANT-Win64-Shipping.exe"

    if not os.path.exists(val_path):
        return False, "Valorant.exe not found at default path."

    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        winreg.SetValueEx(key, val_path, 0, winreg.REG_SZ, "GpuPreference=2;")
        winreg.CloseKey(key)
        return True, "GPU Priority: HIGH PERFORMANCE"
    except Exception as e:
        return False, f"Registry Error: {str(e)}"


def toggle_hags(enable=True):
    path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    value = 2 if enable else 1
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, value)
        winreg.CloseKey(key)
        return True, "HAGS Enabled! (Restart Required)"
    except Exception as e:
        return False, f"Admin Rights Required: {str(e)}"
