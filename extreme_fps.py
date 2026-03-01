import os
import glob


def get_config_path():
    local_appdata = os.getenv('LOCALAPPDATA')
    pattern = os.path.join(local_appdata, "VALORANT", "Saved",
                           "Config", "*", "Windows", "GameUserSettings.ini")
    config_files = glob.glob(pattern)
    return config_files[0] if config_files else None


def apply_extreme_optimizations():
    path = get_config_path()
    if not path:
        return False, "Valorant config not found!"

    # Forced Extreme values + Raw Input Buffer
    settings = {
        "sg.ResolutionQuality": "100.000000",
        "sg.ViewDistanceQuality": "0",
        "sg.AntiAliasingQuality": "0",
        "sg.ShadowQuality": "0",
        "sg.PostProcessQuality": "0",
        "sg.TextureQuality": "0",
        "sg.EffectsQuality": "0",
        "sg.FoliageQuality": "0",
        "sg.ShadingQuality": "0",
        "bRawInputBuffer": "True"
    }

    try:
        with open(path, 'r') as file:
            lines = file.readlines()
        new_lines = [f"{line.split('=')[0]}={settings[line.split('=')[0]]}\n" if line.split(
            '=')[0] in settings else line for line in lines]
        with open(path, 'w') as file:
            file.writelines(new_lines)
        return True, "Extreme FPS & Raw Input Applied!"
    except Exception as e:
        return False, str(e)
