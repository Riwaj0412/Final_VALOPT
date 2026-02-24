import customtkinter as ctk
import valorant_config
import styles
import engine


class ResolutionMenu(ctk.CTkFrame):
    def __init__(self, parent, back_command):
        super().__init__(parent, fg_color="#0f1923")
        self.back_command = back_command
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="VIDEO SETTINGS", font=styles.FONT_ORBITRON_SM,
                     text_color="#ff4655").pack(pady=(0, 20))

        self.menu_container = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_container.pack(pady=10)

        # Fetch Data from engine.py
        supported_res = engine.get_supported_resolutions()
        supported_rates = engine.get_supported_refresh_rates()

        # Resolution Dropdown
        ctk.CTkLabel(self.menu_container, text="RESOLUTION",
                     font=styles.FONT_ORBITRON_SM, text_color="white").pack()
        self.res_dropdown = ctk.CTkOptionMenu(
            self.menu_container, values=supported_res,
            fg_color="#ff4655", button_color="#ff4655", button_hover_color="#d13a45",
            dropdown_fg_color="#0f1923", dropdown_hover_color="#ff4655",
            font=styles.FONT_ORBITRON_SM, width=250, height=40, corner_radius=0
        )
        self.res_dropdown.pack(pady=(5, 20))
        self.res_dropdown.set(supported_res[0])

        # Refresh Rate Dropdown
        ctk.CTkLabel(self.menu_container, text="REFRESH RATE",
                     font=styles.FONT_ORBITRON_SM, text_color="white").pack()
        self.refresh_dropdown = ctk.CTkOptionMenu(
            self.menu_container, values=supported_rates,
            fg_color="#ff4655", button_color="#ff4655", button_hover_color="#d13a45",
            dropdown_fg_color="#0f1923", dropdown_hover_color="#ff4655",
            font=styles.FONT_ORBITRON_SM, width=250, height=40, corner_radius=0
        )
        self.refresh_dropdown.pack(pady=(5, 30))
        self.refresh_dropdown.set(supported_rates[0])

        self.status_label = ctk.CTkLabel(
            self.menu_container, text="", font=styles.FONT_ORBITRON_SM)
        self.status_label.pack(pady=10)

        # Apply Button
        self.apply_btn = ctk.CTkButton(
            self.menu_container, text="CONFIRM SETTINGS",
            fg_color="#ff4655", hover_color="#3498db",
            font=styles.FONT_ORBITRON_SM, width=350, height=50, corner_radius=0,
            command=self.handle_apply
        )
        self.apply_btn.pack(pady=10)

        # Back Button to return to InGameMenu
        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", hover_color="#3498db",
            width=280, height=50, command=self.back_command
        )
        styles.apply_tactical_style(self.back_btn)
        self.back_btn.pack(side="bottom", pady=40)

    def handle_apply(self):
        try:
            res = self.res_dropdown.get()
            w, h = map(int, res.split('x'))
            result = valorant_config.apply_settings(w, h)
            if "SUCCESS" in result:
                self.status_label.configure(
                    text="SETTINGS APPLIED!", text_color="#00ff7f")
            else:
                self.status_label.configure(text=result, text_color="#ff4655")
        except Exception as e:
            self.status_label.configure(
                text=f"ERROR: {e}", text_color="#ff4655")
