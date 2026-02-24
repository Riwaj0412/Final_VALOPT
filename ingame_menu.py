import customtkinter as ctk
import styles
from resolution import ResolutionMenu
from graphics_quality import GraphicsQualityMenu


class InGameMenu(ctk.CTkFrame):
    def __init__(self, parent, back_command):
        super().__init__(parent, fg_color="#0f1923")
        self.parent = parent
        self.original_back_command = back_command
        self.pack(fill="both", expand=True)
        self.show_gate_view()

    def show_gate_view(self):
        self.clear_frame()

        ctk.CTkLabel(self, text="VALOPT", font=styles.FONT_ORBITRON_LG,
                     text_color="#ff4655").pack(pady=(40, 10))

        self.res_gate_btn = ctk.CTkButton(
            self, text="RESOLUTION", font=styles.FONT_ORBITRON_SM,
            width=380, height=60, fg_color="transparent",
            hover_color="#3498db", command=self.open_resolution_file
        )
        styles.apply_tactical_style(self.res_gate_btn)
        self.res_gate_btn.pack(pady=(100, 10))

        self.graphics_gate_btn = ctk.CTkButton(
            self, text="GRAPHICS QUALITY", font=styles.FONT_ORBITRON_SM,
            width=380, height=60, fg_color="transparent",
            hover_color="#3498db", command=self.open_graphics_file
        )
        styles.apply_tactical_style(self.graphics_gate_btn)
        self.graphics_gate_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", hover_color="#3498db",
            width=280, height=50, command=self.original_back_command
        )
        styles.apply_tactical_style(self.back_btn)
        self.back_btn.pack(side="bottom", pady=40)

    def open_resolution_file(self):
        self.clear_frame()
        self.res_menu = ResolutionMenu(self, self.show_gate_view)
        self.res_menu.pack(fill="both", expand=True)

    def open_graphics_file(self):
        self.clear_frame()
        self.graphics_menu = GraphicsQualityMenu(self, self.show_gate_view)
        self.graphics_menu.pack(fill="both", expand=True)

    def clear_frame(self):
        for child in self.winfo_children():
            child.destroy()
