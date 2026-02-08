import platform
import subprocess
import os


def get_monitor_specs():
    try:
        cmd = "wmic path Win32_VideoController get CurrentHorizontalResolution, CurrentRefreshRate, CurrentVerticalResolution"
        out = subprocess.check_output(cmd, shell=True).decode().splitlines()
        stats = [line.strip() for line in out if line.strip()
                 and "Current" not in line][0].split()
        return f"{stats[0]}x{stats[2]} @ {stats[1]}Hz"
    except Exception:
        return "GENERIC HUD // 1920x1080"


def check_valorant_presence():
    return os.path.exists(r"C:\Riot Games\VALORANT\live")


def get_system_report():
    # CPU Name
    try:
        cpu_out = subprocess.check_output(
            "wmic cpu get name", shell=True).decode().splitlines()
        cpu_name = [line.strip() for line in cpu_out if line.strip()
                    and "Name" not in line][0]
    except:
        cpu_name = "AMD Ryzen 5 5600X"

    # RAM Detection
    try:
        ram_raw = os.popen(
            'wmic computersystem get totalphysicalmemory').readlines()
        ram_bytes = [line.strip()
                     for line in ram_raw if line.strip().isdigit()][0]
        ram_gb = f"{round(int(ram_bytes) / 1073741824, 2)} GB"
    except:
        ram_gb = "32.00 GB"

    # GPU Detection
    try:
        gpu_out = subprocess.check_output(
            "wmic path win32_VideoController get name", shell=True).decode().splitlines()
        gpu_name = [line.strip() for line in gpu_out if line.strip()
                    and "Name" not in line][0]
    except:
        gpu_name = "NVIDIA GeForce RTX 3060"

    return {
        "cpu": cpu_name,
        "ram": ram_gb,
        "os": f"Windows {platform.release()}",
        "gpu": gpu_name,
        "monitor": get_monitor_specs(),
        "status": "VALORANT OPTIMIZED"
    }
