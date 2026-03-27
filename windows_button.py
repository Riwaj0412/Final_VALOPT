import subprocess
import re
import socket
import time
import threading
from tkinter import messagebox
import session_logger


# ── Valorant server IPs ────────────────────────────────────────────────────────
# Primary: Riot Direct IPs — these respond to ICMP ping
# Fallback: AWS edge IPs — ICMP blocked, but TCP 2099/443 works
SERVER_IPS = {
    "MUMBAI":      ("151.106.246.1",   "13.126.0.252"),
    "SINGAPORE":   ("151.106.248.1",   "13.228.0.251"),
    "SYDNEY":      ("151.106.30.1",    "13.236.0.253"),
    "TOKYO":       ("151.106.52.1",    "13.112.0.251"),
    "HONG KONG":   ("151.106.54.1",    "18.162.0.252"),
    "LONDON":      ("151.106.38.1",    "3.8.0.252"),
    "FRANKFURT":   ("151.106.34.1",    "3.120.0.252"),
    "PARIS":       ("151.106.35.1",    "13.36.0.252"),
    "MADRID":      ("151.106.36.1",    "15.237.0.252"),
    "ISTANBUL":    ("151.106.58.1",    "3.73.0.252"),
    "N. VIRGINIA": ("151.106.12.1",   "23.23.255.255"),
    "TEXAS":       ("151.106.14.1",   "3.235.255.255"),
    "CALIFORNIA":  ("151.106.16.1",   "13.56.0.252"),
    "SAO PAULO":   ("151.106.24.1",   "15.228.0.252"),
    "MEXICO CITY": ("151.106.20.1",   "15.128.0.252"),
    "SANTIAGO":    ("151.106.26.1",   "54.232.0.252"),
    "SEOUL":       ("151.106.50.1",   "15.164.0.252"),
}

# TCP ports to try as fallback (in order)
_TCP_PORTS = [2099, 443, 80]
_PING_COUNT = 4


# ── ICMP ping ──────────────────────────────────────────────────────────────────
def _icmp_ping(ip: str, count: int = _PING_COUNT) -> int | None:
    try:
        out = subprocess.check_output(
            f"ping {ip} -n {count} -w 2000",
            shell=True,
            stderr=subprocess.DEVNULL,
            creationflags=0x08000000
        ).decode(errors="ignore")

        times = [int(m.group(1)) for m in re.finditer(r"time=(\d+)ms", out)]
        times += [0] * len(re.findall(r"time<1ms", out))

        if times:
            return round(sum(times) / len(times))
    except Exception:
        pass
    return None


# ── TCP connect ping ───────────────────────────────────────────────────────────
def _tcp_ping(ip: str, count: int = 3) -> int | None:
    for port in _TCP_PORTS:
        times = []
        for _ in range(count):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                t0 = time.perf_counter()
                s.connect((ip, port))
                ms = int((time.perf_counter() - t0) * 1000)
                s.close()
                times.append(ms)
            except Exception:
                pass
            time.sleep(0.05)

        if times:
            return round(sum(times) / len(times))

    return None


# ── public API ─────────────────────────────────────────────────────────────────
def get_latency(city_name: str) -> tuple:
    entry = SERVER_IPS.get(city_name.upper())
    if not entry:
        return None, "N/A"

    primary_ip, fallback_ip = entry

    # 1. Try ICMP on Riot Direct IP
    ms = _icmp_ping(primary_ip)
    if ms is not None:
        return ms, f"{ms}ms"

    # 2. Try ICMP on AWS edge IP
    ms = _icmp_ping(fallback_ip)
    if ms is not None:
        return ms, f"{ms}ms"

    # 3. Try TCP on Riot Direct IP
    ms = _tcp_ping(primary_ip)
    if ms is not None:
        return ms, f"{ms}ms"

    # 4. Try TCP on AWS edge IP
    ms = _tcp_ping(fallback_ip)
    if ms is not None:
        return ms, f"{ms}ms"

    return None, "Offline"


def get_best_server() -> tuple:
    results = {}
    lock = threading.Lock()

    def _probe(city, ips):
        primary, fallback = ips
        ms = _icmp_ping(primary, count=2)
        if ms is None:
            ms = _tcp_ping(primary, count=1)
        if ms is None:
            ms = _icmp_ping(fallback, count=2)
        if ms is None:
            ms = _tcp_ping(fallback, count=1)
        if ms is not None:
            with lock:
                results[city] = ms

    threads = [
        threading.Thread(target=_probe, args=(city, ips), daemon=True)
        for city, ips in SERVER_IPS.items()
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)

    if not results:
        return "Unknown", 9999

    best = min(results, key=results.get)
    return best, results[best]


# ── other windows functions ────────────────────────────────────────────────────
def flush_dns():
    try:
        subprocess.check_output(
            "ipconfig /flushdns", shell=True,
            creationflags=0x08000000)
        messagebox.showinfo(
            "VALOPT NETWORK", "DNS Cache Flushed Successfully!")
        session_logger.add_log("Network: DNS cache flushed", "SUCCESS")
        return True
    except Exception as e:
        messagebox.showerror("VALOPT ERROR", f"Failed to flush DNS:\n{e}")
        session_logger.add_log(f"Network: DNS flush failed — {e}", "FAILED")
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
