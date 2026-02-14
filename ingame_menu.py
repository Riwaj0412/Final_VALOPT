import customtkinter as ctk
import valorant_config
import styles
import engine
import ux


class InGameMenu(ctk.CTkFrame):
    def __init__(self, parent, back_command):
        super().__init__(parent, fg_color="#0f1923")
        self.pack(fill="both", expand=True)

        # Header Section
        ctk.CTkLabel(self, text="VALOPT", font=styles.FONT_ORBITRON_LG,
                     text_color="#ff4655").pack(pady=(40, 10))
        ctk.CTkLabel(self, text="VIDEO SETTINGS", font=styles.FONT_ORBITRON_SM,
                     text_color="#ff4655").pack(pady=(0, 40))

        self.menu_container = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_container.pack(pady=10)

        supported_res = engine.get_supported_resolutions()

        # RESOLUTION DROPDOWN
        ctk.CTkLabel(self.menu_container, text="RESOLUTION",
                     font=styles.FONT_ORBITRON_SM, text_color="white").pack()
        self.res_dropdown = ctk.CTkOptionMenu(
            self.menu_container,
            values=supported_res,
            fg_color="#ff4655", button_color="#d13a45", font=styles.FONT_ORBITRON_SM,
            dropdown_font=styles.FONT_ORBITRON_SM, width=350, height=45
        )
        self.res_dropdown.pack(pady=(10, 30))
        if supported_res:
            self.res_dropdown.set(supported_res[0])

        # APPLY BUTTON
        self.apply_btn = ctk.CTkButton(
            self.menu_container, text="CONFIRM SETTINGS",
            fg_color="#ff4655", hover_color="#d13a45",
            font=styles.FONT_ORBITRON_SM, width=350, height=50, corner_radius=0,
            command=self.handle_apply
        )
        self.apply_btn.pack(pady=10)

        # BACK BUTTON
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

            # Execute the config change
            result = valorant_config.apply_settings(w, h)

            # Launch the Tactical Alert
            alert_title = "SYSTEM UPDATE" if "SUCCESS" in result else "CRITICAL ERROR"
            ux.TacticalAlert(self, alert_title, result)

        except Exception as e:
            ux.TacticalAlert(self, "PROCESS ERROR", str(e))
