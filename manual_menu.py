import customtkinter as ctk
import styles
import windows_button
from windows_menu import WindowsMenu  # Make sure to create windows_menu.py next


class ManualMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")

        # 1. Main Title
        self.title_label = ctk.CTkLabel(
            self, text="MANUAL SETTINGS",
            font=styles.FONT_ORBITRON_MD,
            text_color="#ff4655"
        )
        self.title_label.pack(pady=(40, 20))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(expand=True)

        # NVIDIA Button
        self.create_tactical_button("NVIDIA Control Panel", "#76B900", None)

        # WINDOWS Button - Now opens the Sub-Menu
        self.create_tactical_button(
            "WINDOWS",
            "#808080",
            command=self.show_windows_submenu
        )

        # IN GAME Button
        self.create_tactical_button("IN GAME", "#ff4655", None)

        # 2. Unified Back Button
        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", text_color="white", height=60, width=300,
            command=lambda: self.on_back(back_command)
        )
        self.back_btn.pack(side="bottom", pady=40)

    def create_tactical_button(self, text, border_color, command):
        btn = ctk.CTkButton(
            self.button_frame, text=text, font=styles.FONT_ORBITRON_MD,
            width=500, height=80, fg_color="transparent", border_width=2,
            border_color=border_color, text_color="white", command=command
        )
        styles.apply_tactical_style(btn)
        btn.pack(pady=10)
        return btn

    def show_windows_submenu(self):
        """Hides current view to show Windows sub-options"""
        self.button_frame.pack_forget()
        self.title_label.pack_forget()
        self.back_btn.pack_forget()

        self.win_menu = WindowsMenu(self, self.restore_manual_menu)
        self.win_menu.pack(fill="both", expand=True)

    def restore_manual_menu(self):
        """Brings back the Manual Settings buttons"""
        self.title_label.pack(pady=(40, 20))
        self.button_frame.pack(expand=True)
        self.back_btn.pack(side="bottom", pady=40)

    def on_back(self, back_command):
        self.destroy()
        back_command()
