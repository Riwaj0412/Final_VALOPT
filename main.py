import customtkinter as ctk
from splash import SplashScreen
from detected import DetectedScreen
from dashboard import DashboardHUD
import ux


class ValOptApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VALOPT")
        ux.center_window(self, 1000, 850)
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
