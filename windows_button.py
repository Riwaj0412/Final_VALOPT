import subprocess

def open_advanced_display():
    try:
        subprocess.Popen("start ms-settings:display", shell=True)
    except Exception as e:
        print(f"Error: {e}")

def open_hags_settings():
    subprocess.Popen("start ms-settings:display-advancedgraphics", shell=True)

def open_gamebar_settings():
    subprocess.Popen("start ms-settings:gaming-gamemode", shell=True)
