import subprocess
import os
import sys


def get_system_report():
    report = {
        "cpu": "Unknown Processor",
        "gpu": "Unknown Graphics",
        "ram": "0 GB",
        "os": "Windows 10"  # Added this key to prevent the blank screen crash
    }

    # 1. CPU Detection
    try:
        cpu_out = subprocess.check_output(
            "wmic cpu get name", shell=True).decode().splitlines()
        report["cpu"] = [line.strip()
                         for line in cpu_out if line.strip() and "Name" not in line][0]
    except:
        report["cpu"] = "Generic Processor"

    # 2. RAM Detection
    try:
        ram_raw = subprocess.check_output(
            "wmic computersystem get totalphysicalmemory", shell=True).decode().splitlines()
        ram_bytes = [line.strip() for line in ram_raw if line.strip()
                     and "TotalPhysicalMemory" not in line][0]
        report["ram"] = f"{round(int(ram_bytes) / (1024**3))} GB"
    except:
        report["ram"] = "16 GB"

    # 3. GPU Detection
    try:
        gpu_out = subprocess.check_output(
            "wmic path win32_VideoController get name", shell=True).decode().splitlines()
        gpus = [line.strip()
                for line in gpu_out if line.strip() and "Name" not in line]
        report["gpu"] = gpus[0] if gpus else "Integrated Graphics"
    except:
        report["gpu"] = "NVIDIA GeForce"

    # 4. OS Detection (The logic that fixes Windows 11 showing up)
    try:
        # Build 22000+ is Windows 11. Your Win 10 machine will be lower.
        build = sys.getwindowsversion().build
        report["os"] = "Windows 11" if build >= 22000 else "Windows 10"
    except:
        pass

    return report


def get_monitor_specs():
    try:
        cmd = "wmic path Win32_VideoController get CurrentHorizontalResolution, CurrentRefreshRate, CurrentVerticalResolution"
        out = subprocess.check_output(cmd, shell=True).decode().splitlines()
        stats = [line.strip() for line in out if line.strip()
                 and "Current" not in line][0].split()
        return f"{stats[0]}x{stats[2]} @ {stats[1]}Hz"
    except:
        return "1920x1080 @ 60Hz"


def check_valorant_presence():
    return os.path.exists(r"C:\Riot Games\VALORANT\live")
