import customtkinter as ctk
import styles
import windows_button
import power_plan


class WindowsMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")

        # Title
        ctk.CTkLabel(
            self, text="WINDOWS OPTIMIZATION",
            font=styles.FONT_ORBITRON_MD,
            text_color="#ff4655"
        ).pack(pady=(40, 20))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(expand=True)

        # 1. HARDWARE ACCELERATED
        self.create_sub_button("HARDWARE ACCELERATED", "#3d799d",
                               windows_button.open_hags_settings)

        # 2. GAME BAR
        self.create_sub_button("GAME BAR", "#808080",
                               windows_button.open_gamebar_settings)

        # 3. ADVANCED DISPLAY SETTINGS
        self.create_sub_button(
            "ADVANCED DISPLAY SETTINGS",
            "#ff4655",
            windows_button.open_advanced_display
        )

        # 4. MAXIMUM POWER PLAN
        self.create_sub_button(
            "MAXIMUM POWER PLAN",
            "#3d799d",
            self.handle_power_plan
        )

        # Internal Status Message Label
        self.status_label = ctk.CTkLabel(
            self, text="",
            font=styles.FONT_ORBITRON_SM
        )
        self.status_label.pack(pady=10)

        # Back Button
        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", text_color="white", height=60, width=300,
            command=lambda: self.on_back(back_command)
        )
        self.back_btn.pack(side="bottom", pady=40)

    def create_sub_button(self, text, border_color, command):
        btn = ctk.CTkButton(
            self.button_frame, text=text,
            font=styles.FONT_ORBITRON_SM,
            width=500, height=60,
            fg_color="transparent",
            border_width=1,
            border_color=border_color,
            text_color="white",
            command=command
        )
        styles.apply_tactical_style(btn)
        btn.pack(pady=10)

    def handle_power_plan(self):
        """Triggers the logic and provides visual/audio feedback"""
        success = power_plan.set_max_power()
        if success:
            self.status_label.configure(
                text=">> SYSTEM ARMED: POWER MAXIMIZED",
                text_color="#00ff7f"  # Success Green
            )
        else:
            self.status_label.configure(
                text=">> ERROR: OVERRIDE FAILED",
                text_color="#ff4655"  # Error Red
            )

        # Clear the message after 3 seconds
        self.after(3000, lambda: self.status_label.configure(text=""))

    def on_back(self, back_command):
        self.pack_forget()
        back_command()
