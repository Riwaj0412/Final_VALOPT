import customtkinter as ctk
import styles
import optimize_button
from home_menu import HomeMenu
from specs_menu import SpecsMenu


class DashboardHUD(ctk.CTkFrame):
    def __init__(self, master_app):
        super().__init__(master_app, fg_color="#0f1923")
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.master_app = master_app

        ctk.CTkLabel(self, text="V A L O P T", font=styles.FONT_ORBITRON_LG,
                     text_color="#ff4655").pack(pady=(60, 20))

        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True)

        self.show_home()

    def show_home(self):
        for child in self.content_area.winfo_children():
            child.destroy()
        HomeMenu(self.content_area, self.show_specs, self.show_optimize,
                 self.master_app).pack(fill="both", expand=True)

    def show_specs(self):
        for child in self.content_area.winfo_children():
            child.destroy()
        SpecsMenu(self.content_area, self.show_home).pack(
            fill="both", expand=True)

    def show_optimize(self):
        for child in self.content_area.winfo_children():
            child.destroy()
        self.opt_menu_container = self.content_area
        optimize_button.build_optimize_menu(self)
