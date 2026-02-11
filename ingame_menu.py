import customtkinter as ctk
import styles
import valorant_config  # Your logic file


class InGameMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")

        # Title
        self.status_label = ctk.CTkLabel(
            self, text="IN-GAME OPTIMIZATION",
            font=styles.FONT_ORBITRON_MD, text_color="#ff4655"
        )
        self.status_label.pack(pady=(40, 20))

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(expand=True)

        # Resolution Dropdown Label
        ctk.CTkLabel(
            self.content_frame, text="RESOLUTION",
            font=styles.FONT_ORBITRON_SM, text_color="white"
        ).pack(pady=(10, 0))

        # Dropdown Options (X x Y)
        self.res_options = [
            "1920x1080 (16:9)",
            "1600x1200 (4:3)",
            "1280x960 (4:3)",
            "1280x1024 (5:4)",
            "1024x768 (4:3)"
        ]

        self.res_dropdown = ctk.CTkOptionMenu(
            self.content_frame,
            values=self.res_options,
            width=400, height=50,
            font=styles.FONT_ORBITRON_SM,
            fg_color="#1a1a1a",
            button_color="#ff4655",
            button_hover_color="#d13a45",
            dropdown_font=styles.FONT_ORBITRON_SM
        )
        self.res_dropdown.set("1920x1080 (16:9)")  # Default value
        self.res_dropdown.pack(pady=20)

        # Apply Button
        self.apply_btn = ctk.CTkButton(
            self.content_frame, text="APPLY RESOLUTION",
            font=styles.FONT_ORBITRON_SM, width=400, height=60,
            fg_color="transparent", border_width=2, border_color="#ff4655",
            command=self.handle_apply
        )
        self.apply_btn.pack(pady=20)

        # Back Button
        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", height=60, width=300,
            command=back_command
        )
        self.back_btn.pack(side="bottom", pady=40)

    def handle_apply(self):
        # Extract width and height from the selected string (e.g. "1280x960")
        selected = self.res_dropdown.get().split(" ")[0]
        width, height = map(int, selected.split("x"))

        # Call the config logic
        result = valorant_config.apply_stretched_res(width, height)

        if "SUCCESS" in result:
            self.status_label.configure(
                text=f"APPLIED {width}x{height}", text_color="#76B900")
        else:
            self.status_label.configure(text=result, text_color="yellow")
