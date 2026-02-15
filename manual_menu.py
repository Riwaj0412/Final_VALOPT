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

        self.title_label = ctk.CTkLabel(
            self, text="MANUAL SETTINGS",
            font=styles.FONT_ORBITRON_MD,
            text_color="#ff4655"
        )
        self.title_label.pack(pady=(40, 20))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(expand=True, fill="x", padx=50)

        # 1. IN-GAME SETTINGS
        self.create_tactical_button(
            "IN-GAME SETTINGS", "#ff4655", command=self.show_ingame_submenu)

        # 2. NVIDIA Control Panel
        self.create_tactical_button(
            "NVIDIA Control Panel", "#76B900", command=self.show_placeholder_msg)

        # 3. WINDOWS
        self.create_tactical_button(
            "WINDOWS", "#808080", command=self.show_windows_submenu)

        # 4. NETWORK
        self.create_tactical_button(
            "NETWORK", "#3d799d", command=self.show_network_submenu)

        # 5. BACK BUTTON
        self.back_btn = ctk.CTkButton(
            self,
            text="[ BACK ]",
            font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655",
            hover_color="#ff5f6b",
            text_color="white",
            height=60,
            width=300,
            corner_radius=4,
            command=self.back_command
        )
        self.back_btn.pack(side="bottom", pady=40)

        self.current_submenu = None

    def create_tactical_button(self, text, border_color, command):
        btn = ctk.CTkButton(
            self.button_frame,
            text=text,
            font=styles.FONT_ORBITRON_MD,
            width=500,
            height=70,
            fg_color="transparent",
            border_width=1,
            border_color=border_color,
            text_color="white",
            command=command
        )
        styles.apply_tactical_style(btn)
        btn.pack(pady=12, anchor="center")

    def show_placeholder_msg(self):
        messagebox.showinfo("VALOPT", "Working on this feature")

    def show_ingame_submenu(self):
        self.hide_main_content()
        self.current_submenu = InGameMenu(self, self.restore_manual_menu)
        self.current_submenu.pack(fill="both", expand=True)

    def show_windows_submenu(self):
        self.hide_main_content()
        self.current_submenu = WindowsMenu(self, self.restore_manual_menu)
        self.current_submenu.pack(fill="both", expand=True)

    def show_network_submenu(self):
        self.hide_main_content()
        self.current_submenu = NetworkMenu(self, self.restore_manual_menu)
        self.current_submenu.pack(fill="both", expand=True)

    def hide_main_content(self):
        self.title_label.pack_forget()
        self.button_frame.pack_forget()
        self.back_btn.pack_forget()

    def restore_manual_menu(self):
        if self.current_submenu:
            self.current_submenu.destroy()
        self.title_label.pack(pady=(40, 20))
        self.button_frame.pack(expand=True, fill="x", padx=50)
        self.back_btn.pack(side="bottom", pady=40)
