import customtkinter as ctk
import launcher 
import specs_factory
from toggle_logic import toggle_specs

class DashboardHUD(ctk.CTkFrame):
    def __init__(self, master_app):
        super().__init__(master_app, fg_color="#0f1923")
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.is_revealed = False
        self.node_widgets = {}

        # Title
        ctk.CTkLabel(self, text="V A L O P T", font=("Impact", 70), 
                     text_color="#ff4655").pack(pady=(60, 20))

        # Play Button
        self.play_btn = ctk.CTkButton(
            self, text="[ PLAY ]", font=("Arial", 22, "bold"),
            fg_color="transparent", border_color="#00ff7f", border_width=2,
            text_color="#00ff7f", hover_color="#1a3d2e", height=70, width=300,
            command=self.handle_play_click
        )
        self.play_btn.pack(pady=20)

        # Specs Grid Container
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(expand=True, fill="both", padx=50)
        
        # Build the grid (Hidden by default)
        specs_factory.build_specs_grid(self.grid_container, self.node_widgets)

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(pady=40)

        self.reveal_btn = ctk.CTkButton(footer, text="[ REVEAL SPECS ]",
                                        font=("Arial", 18), height=60, width=250,
                                        command=lambda: toggle_specs(self))
        self.reveal_btn.pack(side="left", padx=20)

        ctk.CTkButton(footer, text="[ OPTIMIZE ]", font=("Arial", 18), 
                      fg_color="#ff4655", height=60, width=250).pack(side="left", padx=20)

    def handle_play_click(self):
        self.play_btn.configure(text="[ IN-GAME ]", fg_color="#00ff7f", 
                                text_color="#0f1923", state="disabled")
        launcher.start_game(self.reset_play_button)

    def reset_play_button(self):
        self.after(0, lambda: self.play_btn.configure(
            text="[ PLAY ]", fg_color="transparent", 
            text_color="#00ff7f", state="normal"
        ))