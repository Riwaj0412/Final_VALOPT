import os
import sys
import shutil
import subprocess

# ── config ─────────────────────────────────────────────────────────────────────
APP_NAME = "VALOPT"
ENTRY_POINT = "main.py"
# optional — set to None if you have no icon
ICON_PATH = "assets/icon.ico"
ASSETS_DIR = "assets"
# add ("src_path", "dest_folder") tuples if needed
EXTRA_DATA = []

# ── UAC manifest (requests admin on launch) ────────────────────────────────────
_MANIFEST = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity version="1.0.0.0" processorArchitecture="X86"
    name="{name}" type="win32"/>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>
""".format(name=APP_NAME)

_MANIFEST_PATH = f"{APP_NAME}.manifest"


def write_manifest():
    with open(_MANIFEST_PATH, "w") as f:
        f.write(_MANIFEST)
    print(f"[build] Manifest written → {_MANIFEST_PATH}")


def check_pyinstaller():
    try:
        import PyInstaller
        print(f"[build] PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("[build] PyInstaller not found — installing…")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                       check=True)


def build():
    write_manifest()
    check_pyinstaller()

    # collect assets folder
    datas = []
    if os.path.isdir(ASSETS_DIR):
        datas.append(f"{ASSETS_DIR}{os.pathsep}{ASSETS_DIR}")
    for src, dst in EXTRA_DATA:
        datas.append(f"{src}{os.pathsep}{dst}")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                            # single .exe
        "--windowed",                           # no console window
        f"--name={APP_NAME}",
        f"--manifest={_MANIFEST_PATH}",         # UAC admin request
        # PyInstaller UAC flag (belt+braces)
        "--uac-admin",

        # hidden imports that PyInstaller misses
        "--hidden-import=customtkinter",
        "--hidden-import=psutil",
        "--hidden-import=GPUtil",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",

        # collect entire customtkinter package (it has data files)
        "--collect-all=customtkinter",
    ]

    if os.path.exists(ICON_PATH):
        cmd.append(f"--icon={ICON_PATH}")

    for d in datas:
        cmd.extend(["--add-data", d])

    cmd.append(ENTRY_POINT)

    print(f"\n[build] Running PyInstaller…\n{'─'*60}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        exe_path = os.path.join("dist", f"{APP_NAME}.exe")
        size_mb = os.path.getsize(exe_path) / 1_048_576
        print(f"\n{'─'*60}")
        print(f"[build] ✔  SUCCESS")
        print(f"[build]    Output : {os.path.abspath(exe_path)}")
        print(f"[build]    Size   : {size_mb:.1f} MB")
        print(f"\n[build] Share dist/{APP_NAME}.exe — that's all users need!")
    else:
        print("\n[build] ✖  Build failed — see errors above.")

    # cleanup temp files
    for f in [_MANIFEST_PATH, f"{APP_NAME}.spec"]:
        try:
            os.remove(f)
        except Exception:
            pass
    for d in ["build", "__pycache__"]:
        try:
            shutil.rmtree(d)
        except Exception:
            pass


if __name__ == "__main__":
    build()
