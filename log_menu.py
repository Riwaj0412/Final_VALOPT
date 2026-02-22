import customtkinter as ctk
import styles
import session_logger


class LogMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")

        # Header
        ctk.CTkLabel(self, text="SESSION LOGS", font=styles.FONT_ORBITRON_MD,
                     text_color="#ff4655").pack(pady=(40, 10))
        self.log_box = ctk.CTkTextbox(self,
                                      width=800,
                                      height=350,
                                      font=styles.FONT_ORBITRON_SM,
                                      fg_color="#0a0a0a",
                                      text_color="white",
                                      border_color="#333333",
                                      border_width=1,
                                      wrap="none")
        self.log_box.pack(pady=20, padx=20)

        self.refresh_logs()

        # Action Buttons
        self.restore_btn = ctk.CTkButton(self, text="[ RESTORE DEFAULTS ]",
                                         font=styles.FONT_ORBITRON_SM,
                                         height=60, width=320, command=self.handle_restore)
        styles.apply_tactical_style(self.restore_btn)
        self.restore_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
                                      fg_color="#ff4655", height=60, width=320, command=back_command)
        self.back_btn.pack(side="bottom", pady=40)

    def refresh_logs(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        logs = session_logger.get_logs()

        if not logs:
            self.log_box.insert(
                "1.0", ">> SYSTEM IDLE: NO CHANGES DETECTED...")
        else:
            self.log_box.insert("1.0", "\n".join(logs))

        self.log_box.configure(state="disabled")

    def handle_restore(self):
        session_logger.restore_defaults()
        self.refresh_logs()
