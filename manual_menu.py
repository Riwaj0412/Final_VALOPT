import customtkinter as ctk
import styles
from windows_menu import WindowsMenu
from ingame_menu import InGameMenu


class ManualMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.back_command = back_command

        # Main Title
        self.title_label = ctk.CTkLabel(
            self, text="MANUAL SETTINGS",
            font=styles.FONT_ORBITRON_MD,
            text_color="#ff4655"
        )
        self.title_label.pack(pady=(40, 20))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(expand=True)

        # Main Buttons
        self.create_tactical_button("NVIDIA Control Panel", "#76B900", None)
        self.create_tactical_button(
            "WINDOWS", "#808080", command=self.show_windows_submenu)
        self.create_tactical_button(
            "IN GAME", "#ff4655", command=self.show_ingame_submenu)

        # Global [ BACK ] Button
        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", text_color="white", height=60, width=300,
            corner_radius=4, command=lambda: self.on_back(back_command)
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

    def show_windows_submenu(self):
        """Switches to the Windows Optimization menu"""
        self.hide_main_content()
        self.current_submenu = WindowsMenu(self, self.restore_manual_menu)
        self.current_submenu.pack(fill="both", expand=True)

    def show_ingame_submenu(self):
        """Switches to the In-Game Optimization menu"""
        self.hide_main_content()
        self.current_submenu = InGameMenu(self, self.restore_manual_menu)
        self.current_submenu.pack(fill="both", expand=True)

    def hide_main_content(self):
        self.button_frame.pack_forget()
        self.title_label.pack_forget()
        self.back_btn.pack_forget()

    def restore_manual_menu(self):
        """Brings back the Manual Settings layout"""
        if hasattr(self, 'current_submenu'):
            self.current_submenu.destroy()
        self.title_label.pack(pady=(40, 20))
        self.button_frame.pack(expand=True)
        self.back_btn.pack(side="bottom", pady=40)

    def on_back(self, back_command):
        self.destroy()
        back_command()
