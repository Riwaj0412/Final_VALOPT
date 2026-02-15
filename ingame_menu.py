import customtkinter as ctk
import styles
import session_logger
import valorant_config


class InGameMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")
        self.back_command = back_command

        ctk.CTkLabel(self, text="IN-GAME OPTIMIZATION",
                     font=styles.FONT_ORBITRON_MD, text_color="#ff4655").pack(pady=(40, 20))

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True)

        # Resolution Selection
        ctk.CTkLabel(self.container, text="SELECT RESOLUTION",
                     font=styles.FONT_ORBITRON_SM, text_color="white").pack(pady=5)

        self.res_dropdown = ctk.CTkComboBox(self.container,
                                            values=["1920x1080", "1600x900",
                                                    "1280x720", "1024x768"],
                                            font=styles.FONT_ORBITRON_SM, width=300, height=40)
        self.res_dropdown.pack(pady=10)

        # Apply Button
        self.apply_btn = ctk.CTkButton(self.container, text="[ APPLY SETTINGS ]",
                                       font=styles.FONT_ORBITRON_SM,
                                       width=300, height=60, command=self.handle_apply)
        styles.apply_tactical_style(self.apply_btn)
        self.apply_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(
            self.container, text="", font=styles.FONT_ORBITRON_SM)
        self.status_label.pack(pady=10)

        # Back Button
        self.back_btn = ctk.CTkButton(self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
                                      fg_color="#ff4655", height=60, width=300,
                                      command=self.back_command)
        self.back_btn.pack(side="bottom", pady=40)

    def handle_apply(self):
        try:
            res = self.res_dropdown.get()
            w, h = map(int, res.split('x'))
            result = valorant_config.apply_settings(w, h)

            if "SUCCESS" in result:
                session_logger.add_log(f"Display: Applied Resolution {res}")
                self.status_label.configure(
                    text="SETTINGS APPLIED!", text_color="#00ff7f")
            else:
                self.status_label.configure(
                    text=f"FAILED: {result}", text_color="#ff4655")

        except Exception as e:
            self.status_label.configure(
                text=f"ERROR: {str(e)}", text_color="#ff4655")
            session_logger.add_log(f"Display Error: {str(e)}", "FAILED")
