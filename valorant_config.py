import os
import subprocess
import configparser


def is_valorant_running():
    """Checks if the Valorant process is currently active."""
    try:
        # Tasklist command searches for the specific Valorant shipping process
        output = subprocess.check_output(
            'tasklist', shell=True).decode('utf-8')
        return "VALORANT-Win64-Shipping.exe" in output
    except:
        return False


def apply_stretched_res(width=1280, height=960):
    """Applies resolution only if the game is closed."""
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
                    # Valorant INI files often use case-sensitive keys
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

                        with open(file_path, 'w') as configfile:
                            config.write(
                                configfile, space_around_delimiters=False)
                        return f"SUCCESS: Set to {width}x{height}"
        return "ERROR: Config folder not found."
    except Exception as e:
        return f"ERROR: {str(e)}"
