import customtkinter as ctk
import styles
import os
import glob
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

        # 5. EXTREME FPS (New Button below Network)
        self.extreme_fps_btn = ctk.CTkButton(
            self.button_frame,
            text="EXTREME FPS",
            font=styles.FONT_ORBITRON_MD,
            width=500,
            height=70,
            fg_color="transparent",
            border_width=1,
            border_color="#ff4655",  # Red border
            text_color="#ff4655",   # Red text as requested
            command=self.handle_extreme_fps
        )
        styles.apply_tactical_style(self.extreme_fps_btn)
        self.extreme_fps_btn.pack(pady=12, anchor="center")

        # 6. BACK BUTTON
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

    def handle_extreme_fps(self):
        """Logic to strip Valorant settings to absolute minimum for FPS boost"""
        local_appdata = os.getenv('LOCALAPPDATA')
        pattern = os.path.join(local_appdata, "VALORANT", "Saved",
                               "Config", "*", "Windows", "GameUserSettings.ini")
        config_files = glob.glob(pattern)

        if not config_files:
            messagebox.showerror(
                "VALOPT", "Valorant configuration file not found!")
            return

        # Core settings to force '0' (Extreme Low)
        extreme_settings = {
            "sg.ResolutionQuality": "100.000000",
            "sg.ViewDistanceQuality": "0",
            "sg.AntiAliasingQuality": "0",
            "sg.ShadowQuality": "0",
            "sg.PostProcessQuality": "0",
            "sg.TextureQuality": "0",
            "sg.EffectsQuality": "0",
            "sg.FoliageQuality": "0",
            "sg.ShadingQuality": "0"
        }

        try:
            target_file = config_files[0]
            with open(target_file, 'r') as file:
                lines = file.readlines()

            new_lines = []
            for line in lines:
                modified = False
                for key, value in extreme_settings.items():
                    if line.strip().startswith(key + "="):
                        new_lines.append(f"{key}={value}\n")
                        modified = True
                        break
                if not modified:
                    new_lines.append(line)

            with open(target_file, 'w') as file:
                file.writelines(new_lines)

            messagebox.showinfo(
                "VALOPT", "EXTREME FPS SETTINGS APPLIED!\nRestart Valorant if it is running.")
        except Exception as e:
            messagebox.showerror("VALOPT", f"Error applying settings: {e}")

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
