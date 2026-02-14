import customtkinter as ctk
import styles
import os
from tkinter import messagebox
from windows_menu import WindowsMenu
from ingame_menu import InGameMenu
from network_menu import NetworkMenu


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

        self.create_tactical_button(
            "NVIDIA Control Panel", "#76B900", self.show_placeholder_msg)

        self.create_tactical_button(
            "WINDOWS", "#808080", command=self.show_windows_submenu)

        # NETWORK BUTTON
        self.create_tactical_button(
            "NETWORK", "#3d799d", command=self.show_network_submenu)

        self.create_tactical_button(
            "[ BACK ]", "#ff4655", command=self.back_command)

    def show_placeholder_msg(self):
        """Temporary placeholder to avoid system errors while testing other features"""
        messagebox.showinfo("VALOPT", "Working on this feature")

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

    def show_network_submenu(self):
        self.hide_main_content()
        self.current_submenu = NetworkMenu(self, self.restore_manual_menu)
        self.current_submenu.pack(fill="both", expand=True)

    def hide_main_content(self):
        self.button_frame.pack_forget()
        self.title_label.pack_forget()

    def restore_manual_menu(self):
        if hasattr(self, 'current_submenu'):
            self.current_submenu.pack_forget()
        self.title_label.pack(pady=(40, 20))
        self.button_frame.pack(expand=True)
