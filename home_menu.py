import customtkinter as ctk
import styles
import launcher


class HomeMenu(ctk.CTkFrame):
    def __init__(self, master, show_specs_cmd, show_optimize_cmd, show_logs_cmd, master_app):
        super().__init__(master, fg_color="transparent")

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True)

        # LEFT: PLAY BUTTON
        self.play_btn = ctk.CTkButton(container, text="PLAY", font=("Orbitron", 62, "bold"),
                                      height=250, width=380,
                                      command=lambda: launcher.start_game(master_app.show_dashboard))
        styles.apply_tactical_style(self.play_btn)
        self.play_btn.pack(side="left", padx=20)

        # CENTER: DECORATIVE SLASH
        ctk.CTkLabel(container, text="/", font=("Orbitron", 300),
                     text_color="#ff4655").pack(side="left", padx=15)

        # RIGHT: VERTICAL BUTTON GROUP
        footer = ctk.CTkFrame(container, fg_color="transparent")
        footer.pack(side="left", padx=20)

        # REVEAL SPECS
        self.reveal_btn = ctk.CTkButton(footer, text="REVEAL SPECS", font=styles.FONT_ORBITRON_SM,
                                        height=75, width=280, command=show_specs_cmd)
        styles.apply_tactical_style(self.reveal_btn)
        self.reveal_btn.pack(pady=(0, 10))

        # OPTIMIZE
        self.opt_btn = ctk.CTkButton(footer, text="OPTIMIZE", font=styles.FONT_ORBITRON_SM,
                                     height=75, width=280, command=show_optimize_cmd)
        styles.apply_tactical_style(self.opt_btn)
        self.opt_btn.pack(pady=(0, 10))

        # NEW: SESSION LOG (Placed below Optimize)
        self.log_btn = ctk.CTkButton(footer, text="SESSION LOG", font=styles.FONT_ORBITRON_SM,
                                     height=75, width=280, command=show_logs_cmd)
        styles.apply_tactical_style(self.log_btn)
        self.log_btn.pack(pady=(0, 10))
