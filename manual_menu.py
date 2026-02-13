import customtkinter as ctk
import styles
import os
import subprocess
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

        # Main Buttons - Now with NVIDIA Logic
        self.create_tactical_button(
            "NVIDIA Control Panel", "#76B900", self.open_nvidia_panel)
        self.create_tactical_button(
            "WINDOWS", "#808080", command=self.show_windows_submenu)
        self.create_tactical_button(
            "IN GAME", "#ff4655", command=self.show_ingame_submenu)

        # Global [ BACK ] Button
        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", text_color="white", height=60, width=300,
            corner_radius=4, command=back_command
        )
        self.back_btn.pack(side="bottom", pady=40)

    def open_nvidia_panel(self):
        """Attempts to launch the NVIDIA Control Panel executable."""
        paths = [
            r"C:\Program Files\NVIDIA Corporation\Control Panel Client\nvcplui.exe",
            r"C:\Windows\System32\nvcplui.exe"
        ]

        found = False
        for path in paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                found = True
                break

        if not found:
            # If the .exe isn't found, try the shell command which sometimes works for DCH drivers
            try:
                subprocess.Popen("start nvcplui.exe", shell=True)
            except:
                print("NVIDIA Control Panel not found on this system.")

    def create_tactical_button(self, text, border_color, command):
        btn = ctk.CTkButton(
            self.button_frame, text=text, font=styles.FONT_ORBITRON_MD,
            width=500, height=80, fg_color="transparent", border_width=2,
            border_color=border_color, text_color="white", command=command
        )
        styles.apply_tactical_style(btn)
        btn.pack(pady=10)

    def show_windows_submenu(self):
        self.hide_main_content()
        self.current_submenu = WindowsMenu(self, self.restore_manual_menu)
        self.current_submenu.pack(fill="both", expand=True)

    def show_ingame_submenu(self):
        self.hide_main_content()
        self.current_submenu = InGameMenu(self, self.restore_manual_menu)
        self.current_submenu.pack(fill="both", expand=True)

    def hide_main_content(self):
        self.button_frame.pack_forget()
        self.title_label.pack_forget()
        self.back_btn.pack_forget()

    def restore_manual_menu(self):
        if hasattr(self, 'current_submenu'):
            self.current_submenu.destroy()
        self.title_label.pack(pady=(40, 20))
        self.button_frame.pack(expand=True)
        self.back_btn.pack(side="bottom", pady=40)
