import customtkinter as ctk
import styles


class ManualMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="MANUAL SETTINGS",
            font=styles.FONT_ORBITRON_MD,
            text_color="#ff4655"
        )
        self.title_label.pack(pady=(40, 20))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(expand=True)

        self.create_tactical_button("NVIDIA Control Panel", "#76B900")
        self.create_tactical_button("WINDOWS", "#808080")
        self.create_tactical_button("IN GAME", "#ff4655")

        # --- UNIFIED BACK TO HOME BUTTON ---
        # Changed from CTkLabel to CTkButton for visual consistency
        self.back_btn = ctk.CTkButton(
            self,
            text="[ BACK TO HOME ]",
            font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655",  # Solid Red background
            text_color="white",
            height=60,
            width=300,
            corner_radius=4,
            command=lambda: self.on_back(back_command)
        )
        styles.apply_tactical_style(self.back_btn)
        self.back_btn.pack(side="bottom", pady=40)

    def create_tactical_button(self, text, border_color):
        btn = ctk.CTkButton(
            self.button_frame,
            text=text,
            font=styles.FONT_ORBITRON_MD,
            width=500,
            height=80,
            fg_color="transparent",
            border_width=2,
            border_color=border_color,
            text_color="white"
        )
        styles.apply_tactical_style(btn)
        btn.pack(pady=10)
        return btn

    def on_back(self, back_command):
        self.destroy()
        back_command()
