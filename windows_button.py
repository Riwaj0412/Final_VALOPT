import subprocess
import re
import os
import socket
import time
from tkinter import messagebox
import webbrowser
import session_logger

SERVER_IPS = {
    "MUMBAI": "13.126.0.252",
    "SINGAPORE": "13.228.0.251",
    "SYDNEY": "13.236.0.253",
    "TOKYO": "13.112.0.251",
    "HONG KONG": "18.162.0.252",
    "LONDON": "3.8.0.252",
    "FRANKFURT": "3.120.0.252",
    "PARIS": "13.36.0.252",
    "MADRID": "15.237.0.252",
    "ISTANBUL": "3.73.0.252",
    "N. VIRGINIA": "23.23.255.255",
    "TEXAS": "3.235.255.255",
    "CALIFORNIA": "13.56.0.252",
    "SAO PAULO": "15.228.0.252",
    "MEXICO CITY": "15.128.0.252",
    "SANTIAGO": "54.232.0.252",
    "SEOUL": "15.164.0.252"
}


def get_latency(city_name):
    ip = SERVER_IPS.get(city_name.upper())
    if not ip:
        return "N/A"
    try:
        output = subprocess.check_output(
            f"ping {ip} -n 1 -w 1000", shell=True).decode()
        match = re.search(r"time=(\d+)ms", output)
        if match:
            return f"{match.group(1)}ms"
    except:
        pass
    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        sock.connect((ip, 80))
        ms = int((time.time() - start_time) * 1000)
        sock.close()
        return f"{ms}ms"
    except:
        return "Offline"


def flush_dns():
    try:
        subprocess.check_output("ipconfig /flushdns", shell=True)
        messagebox.showinfo(
            "VALOPT NETWORK", "DNS Cache Flushed Successfully!")
        return True
    except Exception as e:
        messagebox.showerror("VALOPT ERROR", f"Failed to flush DNS:\n{e}")
        return False


def open_advanced_display():
    try:
        subprocess.Popen("start ms-settings:display", shell=True)
    except Exception as e:
        print(f"Error: {e}")
    session_logger.add_log("Windows: Accessed Display/Resolution Settings")


def open_hags_settings():
    subprocess.Popen("start ms-settings:display-advancedgraphics", shell=True)
    session_logger.add_log("Windows: Accessed HAGS Settings")


def open_gamebar_settings():
    subprocess.Popen("start ms-settings:gaming-gamemode", shell=True)
    session_logger.add_log("Windows: Accessed Game Bar Settings")
