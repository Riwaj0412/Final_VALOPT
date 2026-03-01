import customtkinter as ctk
import styles
import os
from tkinter import messagebox
from windows_menu import WindowsMenu
from ingame_menu import InGameMenu
from network_menu import NetworkMenu
import extreme_fps
import ram_cleaner
from session_logger import add_log


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
        self.button_frame.pack(expand=True, fill="both", padx=50)

        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.create_grid_button(
            "IN-GAME SETTINGS", "#ff4655", self.show_ingame_submenu, 0, 0)
        self.create_grid_button("NVIDIA Control Panel",
                                "#76B900", self.show_placeholder_msg, 0, 1)
        self.create_grid_button("WINDOWS", "#808080",
                                self.show_windows_submenu, 1, 0)
        self.create_grid_button("NETWORK", "#3d799d",
                                self.show_network_submenu, 1, 1)

        self.ram_btn = ctk.CTkButton(
            self.button_frame,
            text="CLEAN RAM",
            font=styles.FONT_ORBITRON_SM,
            width=240,
            height=70,
            fg_color="transparent",
            border_width=1,
            border_color="#3498db",
            text_color="white",
            command=self.handle_ram_clean
        )
        styles.apply_tactical_style(self.ram_btn)
        self.ram_btn.grid(row=2, column=0, pady=12, padx=10, sticky="ew")

        self.extreme_fps_btn = ctk.CTkButton(
            self.button_frame,
            text="EXTREME FPS",
            font=styles.FONT_ORBITRON_SM,
            width=240,
            height=70,
            fg_color="transparent",
            border_width=1,
            border_color="#ff4655",
            text_color="#ff4655",
            command=self.handle_extreme_fps
        )
        styles.apply_tactical_style(self.extreme_fps_btn)
        self.extreme_fps_btn.grid(
            row=2, column=1, pady=12, padx=10, sticky="ew")

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

    def create_grid_button(self, text, border_color, command, row, col):
        btn = ctk.CTkButton(
            self.button_frame,
            text=text,
            font=styles.FONT_ORBITRON_SM,
            width=240,
            height=70,
            fg_color="transparent",
            border_width=1,
            border_color=border_color,
            text_color="white",
            command=command
        )
        styles.apply_tactical_style(btn)
        btn.grid(row=row, column=col, pady=12, padx=10, sticky="ew")

    def handle_ram_clean(self):
        cleaned_amount = ram_cleaner.clean_memory()
        if cleaned_amount > 0:
            msg = f"RAM CLEANED: {cleaned_amount}MB Released!"
            add_log(msg, status="SUCCESS")
            messagebox.showinfo("VALOPT", msg)
        else:
            messagebox.showinfo("VALOPT", "RAM is already optimized!")

    def handle_extreme_fps(self):
        confirm = messagebox.askyesno(
            "VALOPT", "Are you sure you want to apply EXTREME FPS settings?")
        if confirm:
            success, message = extreme_fps.apply_extreme_optimizations()
            if success:
                add_log(message, status="SUCCESS")
                messagebox.showinfo("VALOPT", message)
            else:
                add_log("EXTREME FPS FAILED", status="ERROR")
                messagebox.showerror("VALOPT", message)
        else:
            add_log("Extreme FPS optimization cancelled", status="INFO")

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
        self.button_frame.pack(expand=True, fill="both", padx=50)
        self.back_btn.pack(side="bottom", pady=40)
