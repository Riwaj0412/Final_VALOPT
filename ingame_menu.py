import customtkinter as ctk
import styles
import valorant_config


class InGameMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")

        # Header
        self.status_label = ctk.CTkLabel(
            self, text="VIDEO SETTINGS",
            font=styles.FONT_ORBITRON_MD, text_color="#ff4655"
        )
        self.status_label.pack(pady=(40, 20))

        # Container for dropdowns
        self.menu_container = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_container.pack(expand=True, pady=10)

        # --- RESOLUTION SECTION ---
        ctk.CTkLabel(self.menu_container, text="RESOLUTION",
                     font=styles.FONT_ORBITRON_SM, text_color="white").pack()
        self.res_list = valorant_config.get_unique_resolutions()

        self.res_dropdown = ctk.CTkOptionMenu(
            self.menu_container, values=self.res_list,
            width=400, height=45, corner_radius=0,
            fg_color="#0f1923",
            button_color="#ff4655",
            button_hover_color="#d13a45",
            text_color="white",
            dropdown_text_color="white",
            dropdown_fg_color="#0f1923",
            dropdown_hover_color="#ff4655",
            font=styles.FONT_ORBITRON_SM,
            dropdown_font=styles.FONT_ORBITRON_SM,
            command=self.update_refresh_dropdown
        )
        self.res_dropdown.pack(pady=(5, 20))

        # --- REFRESH RATE SECTION ---
        ctk.CTkLabel(self.menu_container, text="REFRESH RATE",
                     font=styles.FONT_ORBITRON_SM, text_color="white").pack()
        self.refresh_dropdown = ctk.CTkOptionMenu(
            self.menu_container, values=[],
            width=400, height=45, corner_radius=0,
            fg_color="#0f1923",
            button_color="#ff4655",
            button_hover_color="#d13a45",
            text_color="white",
            dropdown_text_color="white",
            dropdown_fg_color="#0f1923",
            dropdown_hover_color="#ff4655",
            font=styles.FONT_ORBITRON_SM,
            dropdown_font=styles.FONT_ORBITRON_SM
        )
        self.refresh_dropdown.pack(pady=(5, 20))

        # Initialize refresh rates
        self.update_refresh_dropdown(self.res_list[0])

        # --- CONFIRM BUTTON ---
        self.apply_btn = ctk.CTkButton(
            self.menu_container, text="CONFIRM SETTINGS",
            font=styles.FONT_ORBITRON_SM, width=400, height=50,
            fg_color="#ff4655", hover_color="#d13a45", corner_radius=0,
            text_color="white",
            command=self.handle_apply
        )
        self.apply_btn.pack(pady=20)

        # --- SOLID RED BACK BUTTON ---
        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", hover_color="#d13a45", text_color="white",
            height=60, width=300, corner_radius=4,
            command=back_command
        )
        self.back_btn.pack(side="bottom", pady=40)

    def update_refresh_dropdown(self, selected_res):
        new_rates = valorant_config.get_refresh_rates_for_res(selected_res)
        self.refresh_dropdown.configure(values=new_rates)
        self.refresh_dropdown.set(new_rates[0])

    def handle_apply(self):
        res = self.res_dropdown.get()
        width, height = map(int, res.split('x'))
        result = valorant_config.apply_settings(width, height)

        if "SUCCESS" in result:
            self.status_label.configure(
                text=result.upper(), text_color="#76B900")
        else:
            self.status_label.configure(
                text=result.upper(), text_color="yellow")
