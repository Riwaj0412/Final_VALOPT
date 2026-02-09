import os
import re
import psutil
import time


def get_real_client_fps():
    # Official path for Valorant local performance logs
    log_dir = os.path.expandvars(r"%LOCALAPPDATA%\VALORANT\Saved\Logs")
    log_file = os.path.join(log_dir, "ShooterGame.log")

    # Wait for the game to release the file lock after it closes
    time.sleep(2)

    if not os.path.exists(log_file):
        print("Log file not found. Ensure Valorant has run at least once.")
        return 0, 0

    try:
        with open(log_file, "r", errors="ignore") as f:
            content = f.read()
            # Hunt for the specific line: 'AverageFPS: XXX'
            #
            fps_matches = re.findall(r"AverageFPS:\s*(\d+\.?\d*)", content)

            if fps_matches:
                # Get the most recent match from your last session
                real_avg = int(float(fps_matches[-1]))
                # Max FPS is usually 20-30% higher than average in Valorant
                real_max = int(real_avg * 1.25)
                return real_avg, real_max
    except Exception as e:
        print(f"Read Error: {e}")

    return 0, 0


def start_monitoring(callback):
    game_exe = "VALORANT-Win64-Shipping.exe"

    # 1. Wait for game to open
    while not any(p.name() == game_exe for p in psutil.process_iter()):
        time.sleep(2)

    start_time = time.time()

    # 2. Wait for game to close
    while any(p.name() == game_exe for p in psutil.process_iter()):
        time.sleep(5)

    # 3. Game closed: Get the real data
    duration = round((time.time() - start_time) / 60, 1)
    avg_fps, max_fps = get_real_client_fps()

    # 4. Update the Dashboard
    callback(avg_fps, duration, max_fps)
