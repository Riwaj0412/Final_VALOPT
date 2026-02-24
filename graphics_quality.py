import customtkinter as ctk
import styles


class GraphicsQualityMenu(ctk.CTkFrame):
    def __init__(self, parent, back_command):
        super().__init__(parent, fg_color="#0f1923")
        self.back_command = back_command
        self.selected_quality = None
        self.pack(fill="both", expand=True)
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="VALOPT", font=styles.FONT_ORBITRON_LG,
                     text_color="#ff4655").pack(pady=(40, 40))

        self.btn_container = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_container.pack(pady=20)

        self.low_btn = self.create_quality_btn("LOW")
        self.med_btn = self.create_quality_btn("MEDIUM")
        self.high_btn = self.create_quality_btn("HIGH")

        self.low_btn.pack(side="left", padx=10)
        self.med_btn.pack(side="left", padx=10)
        self.high_btn.pack(side="left", padx=10)

        self.apply_btn = ctk.CTkButton(
            self, text="APPLY SETTINGS", font=styles.FONT_ORBITRON_SM,
            width=350, height=50, fg_color="#ff4655", hover_color="#3498db",
            command=self.handle_apply
        )
        styles.apply_tactical_style(self.apply_btn)
        self.apply_btn.pack(pady=60)

        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            width=280, height=50, fg_color="#ff4655", hover_color="#3498db",
            command=self.back_command
        )
        styles.apply_tactical_style(self.back_btn)
        self.back_btn.pack(side="bottom", pady=40)

    def create_quality_btn(self, label):
        btn = ctk.CTkButton(
            self.btn_container, text=label, font=styles.FONT_ORBITRON_SM,
            width=120, height=60, fg_color="transparent", border_width=2,
            border_color="white", hover_color="#3498db",
            command=lambda: self.select_quality(label)
        )
        return btn

    def select_quality(self, quality):
        self.selected_quality = quality
        for btn in [self.low_btn, self.med_btn, self.high_btn]:
            btn.configure(border_color="white")

        if quality == "LOW":
            self.low_btn.configure(border_color="#ff4655")
        elif quality == "MEDIUM":
            self.med_btn.configure(border_color="#ff4655")
        elif quality == "HIGH":
            self.high_btn.configure(border_color="#ff4655")

    def handle_apply(self):
        if self.selected_quality:
            print(f"Applying {self.selected_quality} settings to config...")
        else:
            print("Please select a quality first.")
