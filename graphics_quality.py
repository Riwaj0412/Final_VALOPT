import customtkinter as ctk
import styles
import os
import glob


class GraphicsQualityMenu(ctk.CTkFrame):
    def __init__(self, parent, back_command):
        super().__init__(parent, fg_color="#0f1923")
        self.back_command = back_command
        self.selected_quality = None
        self.quality_buttons = {}
        self.pack(fill="both", expand=True)
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="VALOPT", font=styles.FONT_ORBITRON_LG,
                     text_color="#ff4655").pack(pady=(40, 10))

        self.btn_container = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_container.pack(pady=40)

        for label in ["LOW", "MEDIUM", "HIGH"]:
            btn = ctk.CTkButton(
                self.btn_container, text=label, font=styles.FONT_ORBITRON_SM,
                width=140, height=60, fg_color="transparent", border_width=2,
                border_color="white", hover_color="#3498db",
                command=lambda l=label: self.select_quality(l)
            )
            styles.apply_tactical_style(btn)
            btn.pack(side="left", padx=15)
            self.quality_buttons[label] = btn

        self.status_label = ctk.CTkLabel(
            self, text="", font=styles.FONT_ORBITRON_SM)
        self.status_label.pack(pady=10)

        self.apply_btn = ctk.CTkButton(
            self, text="APPLY SETTINGS", font=styles.FONT_ORBITRON_SM,
            width=350, height=50, fg_color="#ff4655", hover_color="#3498db",
            command=self.handle_apply
        )
        styles.apply_tactical_style(self.apply_btn)
        self.apply_btn.pack(pady=20)

        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            width=280, height=50, fg_color="#ff4655", hover_color="#3498db",
            command=self.back_command
        )
        styles.apply_tactical_style(self.back_btn)
        self.back_btn.pack(side="bottom", pady=40)

    def select_quality(self, quality):
        self.selected_quality = quality
        for label, btn in self.quality_buttons.items():
            if label == quality:
                btn.configure(fg_color="#ff4655", border_color="#ff4655")
            else:
                btn.configure(fg_color="transparent", border_color="white")
        self.status_label.configure(
            text=f"SELECTED: {quality}", text_color="white")

    def handle_apply(self):
        if not self.selected_quality:
            self.status_label.configure(
                text="PLEASE SELECT A QUALITY FIRST", text_color="#ff4655")
            return

        # Map UI selection to .ini values (0=Low, 1=Med, 2=High)
        val = "0" if self.selected_quality == "LOW" else "1" if self.selected_quality == "MEDIUM" else "2"

        settings_to_change = {
            "sg.ResolutionQuality": "100.000000",
            "sg.ViewDistanceQuality": val,
            "sg.AntiAliasingQuality": val,
            "sg.ShadowQuality": val,
            "sg.PostProcessQuality": val,
            "sg.TextureQuality": val,
            "sg.EffectsQuality": val,
            "sg.FoliageQuality": val,
            "sg.ShadingQuality": val
        }

        # Locating the config file automatically
        local_appdata = os.getenv('LOCALAPPDATA')
        pattern = os.path.join(local_appdata, "VALORANT", "Saved",
                               "Config", "*", "Windows", "GameUserSettings.ini")
        config_files = glob.glob(pattern)

        if not config_files:
            self.status_label.configure(
                text="VALORANT CONFIG NOT FOUND!", text_color="#ff4655")
            return

        target_file = config_files[0]

        try:
            with open(target_file, 'r') as file:
                lines = file.readlines()

            new_lines = []
            for line in lines:
                modified = False
                for key, value in settings_to_change.items():
                    if line.strip().startswith(key + "="):
                        new_lines.append(f"{key}={value}\n")
                        modified = True
                        break
                if not modified:
                    new_lines.append(line)

            with open(target_file, 'w') as file:
                file.writelines(new_lines)

            self.status_label.configure(
                text=f"{self.selected_quality} SETTINGS APPLIED!", text_color="#00ff7f")

        except Exception as e:
            self.status_label.configure(
                text=f"ERROR: {str(e)}", text_color="#ff4655")
