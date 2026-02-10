import customtkinter as ctk
import styles


class ManualMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")

        self.title_label = ctk.CTkLabel(
            self, text="MANUAL SETTINGS",
            font=styles.FONT_ORBITRON_MD,
            text_color="#ff4655"
        )
        self.title_label.pack(pady=(40, 20))

        # Button Container
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(expand=True)

        # Tactical buttons with Orbitron and Red Glow
        self.create_tactical_button("NVIDIA Control Panel", "#76B900")
        self.create_tactical_button("WINDOWS", "#808080")
        self.create_tactical_button("IN GAME", "#ff4655")

        # BACK TO HOME LINK
        self.back_btn = ctk.CTkLabel(
            self, text="[ BACK TO HOME ]",
            font=styles.FONT_ORBITRON_SM,
            text_color="#ff4655",
            cursor="hand2"
        )
        self.back_btn.pack(side="bottom", pady=40)

        # Hover logic
        self.back_btn.bind(
            "<Enter>", lambda e: self.back_btn.configure(text_color="#FF8C94"))
        self.back_btn.bind(
            "<Leave>", lambda e: self.back_btn.configure(text_color="#ff4655"))
        self.back_btn.bind("<Button-1>", lambda e: self.on_back(back_command))

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
