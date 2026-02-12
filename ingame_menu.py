import customtkinter as ctk
import valorant_config
import styles

class InGameMenu(ctk.CTkFrame):
    def __init__(self, parent, back_command):
        super().__init__(parent, fg_color="#0f1923")
        self.pack(fill="both", expand=True)

        # Header Section
        ctk.CTkLabel(self, text="VALOPT", font=styles.FONT_ORBITRON_LG, text_color="#ff4655").pack(pady=(40, 10))
        ctk.CTkLabel(self, text="VIDEO SETTINGS", font=styles.FONT_ORBITRON_SM, text_color="#ff4655").pack(pady=(0, 40))

        self.menu_container = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_container.pack(pady=10)

        # --- RESOLUTION ---
        ctk.CTkLabel(self.menu_container, text="RESOLUTION", font=styles.FONT_ORBITRON_SM, text_color="white").pack()
        self.res_dropdown = ctk.CTkOptionMenu(
            self.menu_container,
            values=["1920x1080", "1280x960", "1024x768"],
            fg_color="#ff4655", button_color="#ff4655", button_hover_color="#d13a45",
            dropdown_fg_color="#0f1923", dropdown_hover_color="#ff4655",
            dropdown_text_color="white",
            font=styles.FONT_ORBITRON_SM,
            dropdown_font=styles.FONT_ORBITRON_SM, 
            width=250, height=40, corner_radius=0
        )
        self.res_dropdown.pack(pady=(5, 20))

        # --- REFRESH RATE ---
        ctk.CTkLabel(self.menu_container, text="REFRESH RATE", font=styles.FONT_ORBITRON_SM, text_color="white").pack()
        self.refresh_dropdown = ctk.CTkOptionMenu(
            self.menu_container,
            values=["165Hz", "144Hz", "60Hz"],
            fg_color="#ff4655", button_color="#ff4655", button_hover_color="#d13a45",
            dropdown_fg_color="#0f1923", dropdown_hover_color="#ff4655",
            dropdown_text_color="white",
            font=styles.FONT_ORBITRON_SM,
            dropdown_font=styles.FONT_ORBITRON_SM, 
            width=250, height=40, corner_radius=0
        )
        self.refresh_dropdown.pack(pady=(5, 30))

        # Status Message
        self.status_label = ctk.CTkLabel(self.menu_container, text="", font=styles.FONT_ORBITRON_SM)
        self.status_label.pack(pady=10)

        # Apply Button
        self.apply_btn = ctk.CTkButton(
            self.menu_container, text="CONFIRM SETTINGS",
            fg_color="#ff4655", hover_color="#d13a45",
            font=styles.FONT_ORBITRON_SM, width=350, height=50, corner_radius=0,
            command=self.handle_apply
        )
        self.apply_btn.pack(pady=10)

        # Back Button
        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", hover_color="#d13a45", corner_radius=4,
            width=280, height=50, command=back_command
        )
        self.back_btn.pack(side="bottom", pady=40)

    def handle_apply(self):
        try:
            res = self.res_dropdown.get()
            w, h = map(int, res.split('x'))
            result = valorant_config.apply_settings(w, h)
            
            color = "#76B900" if "SUCCESS" in result.upper() else "yellow"
            self.status_label.configure(text=result.upper(), text_color=color)
        except Exception as e:
            self.status_label.configure(text=f"ERROR: {str(e)[:20]}", text_color="red")