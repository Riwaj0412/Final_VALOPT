import subprocess
import os

def is_valorant_running():
    try:
        system32 = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32', 'tasklist.exe')
        cmd = system32 if os.path.exists(system32) else "tasklist"
        output = subprocess.check_output(f'"{cmd}" /FI "IMAGENAME eq VALORANT-Win64-Shipping.exe"', shell=True).decode('utf-8', errors='ignore')
        return "VALORANT-Win64-Shipping.exe" in output
    except:
        return False

def get_config_path():
    # Improved search for the specific Riot user folder
    local_appdata = os.environ.get('LOCALAPPDATA')
    if not local_appdata: return None
    
    config_root = os.path.join(local_appdata, 'VALORANT', 'Saved', 'Config')
    if not os.path.exists(config_root): return None

    # Valorant uses random-string folder names; we search all of them for the Windows folder
    for folder in os.listdir(config_root):
        path = os.path.join(config_root, folder, 'Windows', 'GameUserSettings.ini')
        if os.path.exists(path):
            return path
    return None

def apply_settings(width, height):
    if is_valorant_running():
        return "ERROR: CLOSE VALORANT FIRST"

    path = get_config_path()
    if not path:
        return "ERROR: CONFIG FILE NOT FOUND"

    try:
        with open(path, 'r') as f:
            lines = f.readlines()

        updates = {
            'ResolutionSizeX': width, 'ResolutionSizeY': height,
            'LastUserConfirmedResolutionSizeX': width, 'LastUserConfirmedResolutionSizeY': height,
            'FullscreenMode': 0, 'PreferredFullscreenMode': 0
        }

        new_lines = []
        for line in lines:
            matched = False
            for key, val in updates.items():
                if line.strip().startswith(key + "="):
                    new_lines.append(f"{key}={val}\n")
                    matched = True
                    break
            if not matched:
                new_lines.append(line)

        with open(path, 'w') as f:
            f.writelines(new_lines)
        return "SUCCESS: SETTINGS APPLIED"
    except Exception as e:
        return f"ERROR: {str(e)}"

def get_refresh_rates_for_res(res_str):
    return ["165Hz", "144Hz", "120Hz", "60Hz"]