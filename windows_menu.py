import customtkinter as ctk
import styles
import windows_button
import power_plan


class WindowsMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(self, text="WINDOWS OPTIMIZATION",
                     font=styles.FONT_ORBITRON_MD, text_color="#ff4655").pack(pady=(40, 20))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(expand=True)

        # Standard Buttons
        self.create_sub_button("HARDWARE ACCELERATED",
                               "#3d799d", windows_button.open_hags_settings)
        self.create_sub_button("GAME BAR", "#808080",
                               windows_button.open_gamebar_settings)
        self.create_sub_button("ADVANCED DISPLAY SETTINGS",
                               "#ff4655", windows_button.open_advanced_display)

        # MAXIMUM POWER PLAN - linked to the tracker
        self.create_sub_button("MAXIMUM POWER PLAN",
                               "#3d799d", self.apply_power)

        self.status_label = ctk.CTkLabel(
            self, text="", font=styles.FONT_ORBITRON_SM)
        self.status_label.pack(pady=10)

        self.back_btn = ctk.CTkButton(self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
                                      fg_color="#ff4655", height=60, width=300,
                                      command=back_command)
        self.back_btn.pack(side="bottom", pady=40)

    def create_sub_button(self, text, border_color, command):
        btn = ctk.CTkButton(self.button_frame, text=text, font=styles.FONT_ORBITRON_SM,
                            width=500, height=60, border_width=1, border_color=border_color,
                            command=command)
        styles.apply_tactical_style(btn)
        btn.pack(pady=10)

    def apply_power(self):
        if power_plan.set_max_power():
            self.status_label.configure(
                text=">> SYSTEM ARMED", text_color="#00ff7f")
        else:
            self.status_label.configure(
                text=">> ERROR DETECTED", text_color="#ff4655")
        self.after(3000, lambda: self.status_label.configure(text=""))
