import customtkinter as ctk
import styles
import os
import subprocess
from windows_menu import WindowsMenu
from ingame_menu import InGameMenu
from network_menu import NetworkMenu  # Import the new network menu


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
        self.create_tactical_button(
            "NVIDIA Control Panel", "#76B900", self.open_nvidia_panel)

        self.create_tactical_button(
            "WINDOWS", "#808080", command=self.show_windows_submenu)

        # NEW NETWORK BUTTON - Styled to match others
        self.create_tactical_button(
            "NETWORK", "#3d799d", command=self.show_network_submenu)

        self.create_tactical_button(
            "IN GAME", "#ff4655", command=self.show_ingame_submenu)

        # Global [ BACK ] Button
        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", hover_color="#d13a45", corner_radius=4,
            width=280, height=50, command=back_command
        )
        self.back_btn.pack(side="bottom", pady=40)

        self.current_submenu = None

    def open_nvidia_panel(self):
        """Attempts to open NVIDIA Control Panel using common paths"""
        paths = [
            r"C:\Program Files\NVIDIA Corporation\Control Panel Client\nvcplui.exe",
            r"C:\Windows\System32\nvcplui.exe"
        ]
        found = False
        for p in paths:
            if os.path.exists(p):
                subprocess.Popen(p)
                found = True
                break

        if not found:
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

    # NEW: Logic to show the Network Menu
    def show_network_submenu(self):
        self.hide_main_content()
        self.current_submenu = NetworkMenu(self, self.restore_manual_menu)
        self.current_submenu.pack(fill="both", expand=True)

    def hide_main_content(self):
        self.button_frame.pack_forget()
        self.title_label.pack_forget()
        self.back_btn.pack_forget()

    def restore_manual_menu(self):
        if self.current_submenu:
            self.current_submenu.destroy()
        self.title_label.pack(pady=(40, 20))
        self.button_frame.pack(expand=True)
        self.back_btn.pack(side="bottom", pady=40)
