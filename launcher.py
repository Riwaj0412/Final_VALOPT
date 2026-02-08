import subprocess
import psutil
import time
import threading

def start_game(callback):
    # Standard Riot Path
    path = r"C:\Riot Games\Riot Client\RiotClientServices.exe"
    cmd = f'"{path}" --launch-product=valorant --launch-patchline=live'
    
    try:
        subprocess.Popen(cmd, shell=True)
        threading.Thread(target=monitor_game, args=(callback,), daemon=True).start()
    except Exception as e:
        print(f"Error: {e}")
        callback()

def monitor_game(callback):
    # Phase 1: Wait for game to start
    game_proc = None
    while not game_proc:
        for p in psutil.process_iter(['name']):
            if p.info['name'] == "VALORANT-Win64-Shipping.exe":
                game_proc = p
                break
        time.sleep(2)
    
    # Phase 2: Wait for game to close
    while game_proc.is_running():
        time.sleep(5)
        
    callback()