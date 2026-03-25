from installer import run_if_needed
import sys
import ctypes
import customtkinter as ctk
from splash import SplashScreen
from detected import DetectedScreen
from dashboard import DashboardHUD
import ux

# ─────────────────────────────────────────────────────────────────────────────
#  Working Main File
# ─────────────────────────────────────────────────────────────────────────────


def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _relaunch_as_admin():
    if getattr(sys, "frozen", False):
        target = sys.executable
        params = ""
    else:
        target = sys.executable
        params = f'"{sys.argv[0]}"'

    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", target, params, None, 1)
        if ret > 32:
            sys.exit(0)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__" and not _is_admin():
    _relaunch_as_admin()

run_if_needed()


class ValOptApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VALOPT")
        ux.center_window(self, 1000, 900)
        self.resizable(False, False)
        self.stored_data = {}
        self.show_splash()

    def show_splash(self):
        SplashScreen(self, self.show_detected)

    def show_detected(self, data):
        self.stored_data = data
        for child in self.winfo_children():
            child.destroy()
        DetectedScreen(self, self.show_dashboard)

    def show_dashboard(self):
        for child in self.winfo_children():
            child.destroy()
        DashboardHUD(self)


if __name__ == "__main__":
    app = ValOptApp()
    app.mainloop()
