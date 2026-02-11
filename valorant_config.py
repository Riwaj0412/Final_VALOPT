import win32api
import win32con
import os
import subprocess
import configparser


def get_unique_resolutions():
    """Returns a list of unique 'WidthxHeight' strings supported by the monitor."""
    resolutions = set()
    i = 0
    try:
        while True:
            ds = win32api.EnumDisplaySettings(None, i)
            resolutions.add(f"{ds.PelsWidth}x{ds.PelsHeight}")
            i += 1
    except:
        pass
    return sorted(list(resolutions), key=lambda x: int(x.split('x')[0]), reverse=True)


def get_refresh_rates_for_res(resolution_str):
    """Returns all refresh rates supported by a specific resolution (e.g., '2560x1440')."""
    width, height = map(int, resolution_str.split('x'))
    refresh_rates = set()
    i = 0
    try:
        while True:
            ds = win32api.EnumDisplaySettings(None, i)
            if ds.PelsWidth == width and ds.PelsHeight == height:
                refresh_rates.add(f"{ds.DisplayFrequency}Hz")
            i += 1
    except:
        pass
    return sorted(list(refresh_rates), key=lambda x: int(x.replace('Hz', '')), reverse=True)


def apply_settings(width, height):
    """Writes the selected resolution to the Valorant config file."""
    if is_valorant_running():
        return "ERROR: Close Valorant first!"

    path = os.path.expandvars(r'%LOCALAPPDATA%\VALORANT\Saved\Config')
    try:
        for folder in os.listdir(path):
            if "-" in folder:
                file_path = os.path.join(
                    path, folder, "Windows", "GameUserSettings.ini")
                if os.path.exists(file_path):
                    config = configparser.ConfigParser()
                    config.optionxform = str
                    config.read(file_path)
                    section = '/Script/ShooterGame.ShooterGameUserSettings'
                    if config.has_section(section):
                        config.set(section, 'ResolutionSizeX', str(width))
                        config.set(section, 'ResolutionSizeY', str(height))
                        config.set(
                            section, 'LastUserConfirmedResolutionSizeX', str(width))
                        config.set(
                            section, 'LastUserConfirmedResolutionSizeY', str(height))
                        config.set(section, 'FullscreenMode', '0')
                        with open(file_path, 'w') as f:
                            config.write(f, space_around_delimiters=False)
                        return f"SUCCESS: {width}x{height} applied"
        return "ERROR: Config not found"
    except Exception as e:
        return f"ERROR: {str(e)}"


def is_valorant_running():
    output = subprocess.check_output(
        'tasklist', shell=True).decode('utf-8', errors='ignore')
    return "VALORANT-Win64-Shipping.exe" in output
