import os
import sys
import shutil
import subprocess

APP_NAME = "VALOPT"
ENTRY_POINT = "main.py"
ICON_PATH = os.path.join("assets", "icon.ico")

HIDDEN_IMPORTS = [
    "customtkinter",
    "psutil",
    "GPUtil",
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",
    "splash",
    "detected",
    "dashboard",
    "ux",
    "styles",
    "home_menu",
    "log_menu",
    "manual_menu",
    "ingame_menu",
    "graphics_quality",
    "network_menu",
    "windows_button",
    "resolution",
    "priority",
    "ram_cleaner",
    "extreme_fps",
    "power_plan",
    "optimize_button",
    "recommended",
    "benchmark",
    "benchmark_data",
    "fps_reader",
    "session_logger",
    "specs_menu",
    "specs_factory",
    "engine",
    "monitor",
    "launcher",
    "toggle_logic",
    "installer",
    "valorant_config",
    "windows_menu",
]

# UAC manifest — elevates on launch, embedded into the exe
_MANIFEST = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity version="1.0.0.0" processorArchitecture="AMD64"
    name="VALOPT" type="win32"/>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>
"""
_MANIFEST_FILE = "VALOPT.manifest"


def check_pyinstaller():
    try:
        import PyInstaller
        print(f"[ok] PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("[..] Installing PyInstaller...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            check=True)
        print("[ok] PyInstaller installed")


def build():
    print("\n" + "="*50)
    print("  VALOPT BUILD")
    print("="*50 + "\n")

    check_pyinstaller()

    with open(_MANIFEST_FILE, "w") as f:
        f.write(_MANIFEST)

    sep = ";" if sys.platform == "win32" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--noconsole",
        f"--name={APP_NAME}",

        f"--manifest={_MANIFEST_FILE}",
        "--uac-admin",

        "--collect-all=customtkinter",
        "--collect-all=darkdetect",
    ]

    if os.path.exists(ICON_PATH):
        cmd += [f"--icon={ICON_PATH}"]
        print(f"[ok] Icon: {ICON_PATH}")
    else:
        print(f"[--] No icon found at {ICON_PATH}, skipping")

    for imp in HIDDEN_IMPORTS:
        cmd += ["--hidden-import", imp]

    if os.path.isdir("assets"):
        cmd += ["--add-data", f"assets{sep}assets"]
        print("[ok] Bundling assets/")

    cmd.append(ENTRY_POINT)

    print("\n[..] Running PyInstaller (1-3 min)...\n")
    result = subprocess.run(cmd)

    for f in [_MANIFEST_FILE, f"{APP_NAME}.spec"]:
        try:
            os.remove(f)
        except Exception:
            pass
    try:
        shutil.rmtree("build")
    except Exception:
        pass

    print("\n" + "="*50)
    if result.returncode == 0:
        exe = os.path.abspath(os.path.join("dist", f"{APP_NAME}.exe"))
        mb = os.path.getsize(exe) / 1_048_576
        print(f"  BUILD SUCCESS")
        print(f"  File : {exe}")
        print(f"  Size : {mb:.0f} MB")
        print(f"\n  Share dist/VALOPT.exe with your users.")
        print(f"  They need nothing else installed.")
    else:
        print("  BUILD FAILED")
        print("\n  Fix checklist:")
        print("  1. Run this from inside your VALOPT project folder")
        print("  2. Make sure all imports work:  python main.py")
        print("  3. pip install pyinstaller customtkinter psutil GPUtil Pillow")
    print("="*50 + "\n")


if __name__ == "__main__":
    build()
