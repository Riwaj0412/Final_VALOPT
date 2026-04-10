import os
import sys
import json
import subprocess
import threading
import ctypes
import customtkinter as ctk

# ── State storage — tries file first, registry as fallback ────────────────────
_DATA_DIR = os.path.join(
    os.getenv("LOCALAPPDATA", os.path.expanduser("~")), "VALOPT")
_STATE_FILE = os.path.join(_DATA_DIR, "install_state.json")
_REG_KEY = r"SOFTWARE\VALOPT"
_REG_VAL = "InstallComplete"

_RED = "#ff4655"
_DARK = "#0f0f0f"
_GREEN = "#00c853"
_WHITE = "#ffffff"
_MUTED = "#555555"
_PANEL = "#1a1a1a"

_REQUIRED_PACKAGES = [
    ("customtkinter", "customtkinter"),
    ("psutil",        "psutil"),
    ("GPUtil",        "GPUtil"),
    ("Pillow",        "PIL"),
]


# ── State helpers ──────────────────────────────────────────────────────────────
def _mark_done():
    # Try JSON
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(_STATE_FILE, "w") as f:
            json.dump({"install_complete": True}, f)
        return
    except Exception:
        pass
    # Fallback: registry
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, _REG_KEY)
        winreg.SetValueEx(key, _REG_VAL, 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except Exception:
        pass


def _is_done() -> bool:
    # JSON
    try:
        with open(_STATE_FILE, "r") as f:
            data = json.load(f)
        if data.get("install_complete"):
            return True
    except Exception:
        pass
    # Registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY)
        val, _ = winreg.QueryValueEx(key, _REG_VAL)
        winreg.CloseKey(key)
        return bool(val)
    except Exception:
        pass
    return False


def is_first_run() -> bool:
    return not _is_done()


# ── Install helpers ────────────────────────────────────────────────────────────
def _pip_install(pip_name: str) -> bool:
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name, "--quiet"],
            capture_output=True, timeout=120)
        return r.returncode == 0
    except Exception:
        return False


def _pkg_ok(import_name: str) -> bool:
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def _rtss_installed() -> bool:
    paths = [
        r"C:\Program Files\RivaTuner Statistics Server\RTSS.exe",
        r"C:\Program Files (x86)\RivaTuner Statistics Server\RTSS.exe",
        r"C:\Program Files (x86)\MSI Afterburner\Bundle\RTSS\RTSS.exe",
    ]
    return any(os.path.exists(p) for p in paths)


def _install_rtss() -> bool:
    try:
        r = subprocess.run(
            ["winget", "install", "-e", "--id", "Guru3D.RTSS",
             "--accept-package-agreements", "--accept-source-agreements", "--silent"],
            capture_output=True, timeout=180)
        return r.returncode == 0
    except Exception:
        return False


def _launch_rtss():
    for p in [
        r"C:\Program Files\RivaTuner Statistics Server\RTSS.exe",
        r"C:\Program Files (x86)\RivaTuner Statistics Server\RTSS.exe",
    ]:
        if os.path.exists(p):
            try:
                subprocess.Popen([p], creationflags=0x08000000)
            except Exception:
                pass
            return


# ── Installer UI ───────────────────────────────────────────────────────────────
class InstallerWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VALOPT — Setup")
        self.geometry("520x360")
        self.configure(fg_color=_DARK)
        self.resizable(False, False)
        self._center()

        ctk.CTkLabel(self, text="VALOPT",
                     font=("Orbitron", 34, "bold"),
                     text_color=_RED).pack(pady=(28, 2))
        ctk.CTkLabel(self, text="FIRST RUN SETUP",
                     font=("Orbitron", 13), text_color=_WHITE).pack(pady=(0, 16))

        self._status = ctk.CTkLabel(self, text="Preparing…",
                                    font=("Orbitron", 12), text_color=_MUTED)
        self._status.pack(pady=(0, 6))

        self._bar = ctk.CTkProgressBar(self, width=420, height=12,
                                       fg_color=_PANEL, progress_color=_RED)
        self._bar.pack(pady=(0, 10))
        self._bar.set(0)

        self._log = ctk.CTkTextbox(self, width=460, height=130,
                                   fg_color=_PANEL, font=("Consolas", 11),
                                   text_color=_MUTED, state="disabled")
        self._log.pack(pady=(0, 14))

        self._btn = ctk.CTkButton(self, text="Please wait…",
                                  font=("Orbitron", 13, "bold"),
                                  fg_color=_MUTED, hover_color=_MUTED,
                                  text_color=_WHITE, height=44, width=200,
                                  state="disabled", command=self.destroy)
        self._btn.pack()

        threading.Thread(target=self._run, daemon=True).start()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"520x360+{(sw-520)//2}+{(sh-360)//2}")

    def _log_line(self, msg):
        self._log.configure(state="normal")
        self._log.insert("end", msg + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _run(self):
        steps = len(_REQUIRED_PACKAGES) + 1
        done = 0

        for pip_name, import_name in _REQUIRED_PACKAGES:
            self.after(0, lambda p=pip_name: self._status.configure(
                text=f"Checking {p}…"))
            if _pkg_ok(import_name):
                self.after(0, lambda p=pip_name: self._log_line(f"  ✔  {p}"))
            else:
                self.after(0, lambda p=pip_name: self._log_line(
                    f"  ↓  Installing {p}…"))
                ok = _pip_install(pip_name)
                self.after(0, lambda p=pip_name, o=ok: self._log_line(
                    f"  ✔  {p} installed" if o else f"  ⚠  {p} failed"))
            done += 1
            self.after(0, lambda d=done, s=steps: self._bar.set(d / s))

        # RTSS
        self.after(0, lambda: self._status.configure(text="Checking RTSS…"))
        if _rtss_installed():
            self.after(0, lambda: self._log_line(
                "  ✔  RTSS already installed"))
            _launch_rtss()
        else:
            self.after(0, lambda: self._log_line(
                "  ↓  Installing RTSS via winget…"))
            ok = _install_rtss()
            if ok:
                self.after(0, lambda: self._log_line("  ✔  RTSS installed"))
                _launch_rtss()
            else:
                self.after(0, lambda: self._log_line(
                    "  ⚠  RTSS auto-install failed\n"
                    "     Install manually for FPS benchmark:\n"
                    "     guru3d.com/download/rtss-rivatuner-statistics-server-download"))
        done += 1
        self.after(0, lambda: self._bar.set(1.0))

        # Mark done BEFORE closing — this is what prevents the infinite loop
        _mark_done()

        self.after(0, lambda: (
            self._status.configure(text="Setup complete!", text_color=_GREEN),
            self._log_line("\n  ✔  Ready — launching VALOPT"),
            self._btn.configure(text="LAUNCH", fg_color=_GREEN,
                                hover_color="#00a846", state="normal")
        ))


# ── Public entry point ─────────────────────────────────────────────────────────
_ran = False


def run_if_needed():
    global _ran
    if _ran:
        return
    _ran = True

    if not is_first_run():
        return

    win = InstallerWindow()
    win.mainloop()
