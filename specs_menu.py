import customtkinter as ctk
import styles
import specs_factory


class SpecsMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")

        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(expand=True, fill="both", padx=50)

        self.node_widgets = {}
        specs_factory.build_specs_grid(self.grid_container, self.node_widgets)

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
            command=back_command
        )
        self.back_btn.pack(side="bottom", pady=40)
