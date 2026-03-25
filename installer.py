import os
import sys
import json
import subprocess
import threading
import importlib
import ctypes
import customtkinter as ctk

_STATE_FILE = os.path.join(
    os.getenv("LOCALAPPDATA", ""), "VALOPT", "install_state.json")

_REQUIRED_PACKAGES = [
    "customtkinter",
    "psutil",
    "GPUtil",
    "Pillow",
]

_RED = "#ff4655"
_DARK = "#0f0f0f"
_GREEN = "#00c853"
_WHITE = "#ffffff"
_MUTED = "#555555"
_PANEL = "#1a1a1a"


# ── state helpers ──────────────────────────────────────────────────────────────
def _load_state() -> dict:
    try:
        with open(_STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(data: dict):
    os.makedirs(os.path.dirname(_STATE_FILE), exist_ok=True)
    with open(_STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def is_first_run() -> bool:
    return not _load_state().get("install_complete", False)


# ── install logic ──────────────────────────────────────────────────────────────
def _pip_install(package: str) -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package, "--quiet"],
            capture_output=True, timeout=120)
        return result.returncode == 0
    except Exception:
        return False


def _is_package_installed(package: str) -> bool:
    try:
        importlib.import_module(package.lower().replace("-", "_"))
        return True
    except ImportError:
        return False


def _is_rtss_installed() -> bool:
    paths = [
        r"C:\Program Files\RivaTuner Statistics Server\RTSS.exe",
        r"C:\Program Files (x86)\RivaTuner Statistics Server\RTSS.exe",
        r"C:\Program Files (x86)\MSI Afterburner\Bundle\RTSS\RTSS.exe",
        r"C:\Program Files\MSI Afterburner\Bundle\RTSS\RTSS.exe",
    ]
    return any(os.path.exists(p) for p in paths)


def _install_rtss_winget() -> bool:
    try:
        result = subprocess.run(
            ["winget", "install", "-e", "--id", "Guru3D.RTSS",
             "--accept-package-agreements", "--accept-source-agreements",
             "--silent"],
            capture_output=True, timeout=180)
        return result.returncode == 0
    except Exception:
        return False


def _launch_rtss():
    paths = [
        r"C:\Program Files\RivaTuner Statistics Server\RTSS.exe",
        r"C:\Program Files (x86)\RivaTuner Statistics Server\RTSS.exe",
        r"C:\Program Files (x86)\MSI Afterburner\Bundle\RTSS\RTSS.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                subprocess.Popen([p], creationflags=0x08000000)
            except Exception:
                pass
            return


# ── installer UI ───────────────────────────────────────────────────────────────
class InstallerWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VALOPT — Setup")
        self.geometry("520x380")
        self.configure(fg_color=_DARK)
        self.resizable(False, False)
        self._center()
        self._done = False

        ctk.CTkLabel(self, text="VALOPT",
                     font=("Orbitron", 36, "bold"),
                     text_color=_RED).pack(pady=(30, 4))

        ctk.CTkLabel(self, text="FIRST RUN SETUP",
                     font=("Orbitron", 14),
                     text_color=_WHITE).pack(pady=(0, 20))

        self._status = ctk.CTkLabel(
            self, text="Preparing…",
            font=("Orbitron", 12), text_color=_MUTED)
        self._status.pack(pady=(0, 8))

        self._progress = ctk.CTkProgressBar(
            self, width=400, height=14,
            fg_color=_PANEL,
            progress_color=_RED)
        self._progress.pack(pady=(0, 12))
        self._progress.set(0)

        self._log = ctk.CTkTextbox(
            self, width=460, height=140,
            fg_color=_PANEL,
            font=("Consolas", 11),
            text_color=_MUTED,
            state="disabled")
        self._log.pack(pady=(0, 16))

        self._btn = ctk.CTkButton(
            self, text="Please wait…",
            font=("Orbitron", 13, "bold"),
            fg_color=_MUTED, hover_color=_MUTED,
            text_color=_WHITE, height=44, width=200,
            state="disabled", command=self._finish)
        self._btn.pack()

        threading.Thread(target=self._run_install, daemon=True).start()

    def _center(self):
        self.update_idletasks()
        w, h = 520, 380
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _log_line(self, msg: str):
        self._log.configure(state="normal")
        self._log.insert("end", msg + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _set_status(self, msg: str, color: str = _MUTED):
        self._status.configure(text=msg, text_color=color)

    def _run_install(self):
        # packages + RTSS check + finalize
        steps = len(_REQUIRED_PACKAGES) + 2
        done = 0

        # ── 1. Python packages ─────────────────────────────────────────────────
        for pkg in _REQUIRED_PACKAGES:
            self.after(0, lambda p=pkg: self._set_status(f"Checking {p}…"))
            if _is_package_installed(pkg):
                self.after(0, lambda p=pkg: self._log_line(
                    f"  ✔  {p} already installed"))
            else:
                self.after(0, lambda p=pkg: (
                    self._set_status(f"Installing {p}…", _RED),
                    self._log_line(f"  ↓  Installing {p}…")
                ))
                ok = _pip_install(pkg)
                msg = f"  ✔  {pkg} installed" if ok else f"  ⚠  {pkg} failed (may still work)"
                self.after(0, lambda m=msg: self._log_line(m))

            done += 1
            self.after(0, lambda d=done, s=steps: self._progress.set(d / s))

        # ── 2. RTSS ────────────────────────────────────────────────────────────
        self.after(0, lambda: self._set_status("Checking RTSS…"))
        if _is_rtss_installed():
            self.after(0, lambda: self._log_line(
                "  ✔  RTSS already installed"))
            _launch_rtss()
        else:
            self.after(0, lambda: (
                self._set_status("Installing RTSS via winget…", _RED),
                self._log_line("  ↓  Installing RivaTuner Statistics Server…")
            ))
            ok = _install_rtss_winget()
            if ok:
                self.after(0, lambda: self._log_line(
                    "  ✔  RTSS installed successfully"))
                _launch_rtss()
            else:
                self.after(0, lambda: self._log_line(
                    "  ⚠  Auto-install failed.\n"
                    "     Please install manually: guru3d.com/download/rtss-rivatuner-statistics-server-download"
                ))

        done += 1
        self.after(0, lambda: self._progress.set(done / steps))

        # ── 3. Mark complete ───────────────────────────────────────────────────
        _save_state({"install_complete": True})
        done += 1
        self.after(0, lambda: self._progress.set(1.0))
        self.after(0, lambda: (
            self._set_status("Setup complete!", _GREEN),
            self._log_line("\n  ✔  All done — launching VALOPT…"),
            self._btn.configure(
                text="LAUNCH VALOPT",
                fg_color=_GREEN,
                hover_color="#00a846",
                state="normal")
        ))

    def _finish(self):
        self._done = True
        self.destroy()


def run_if_needed():
    if not is_first_run():
        return

    app = InstallerWindow()
    app.mainloop()
