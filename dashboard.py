import customtkinter as ctk
import launcher
import specs_factory
import optimize_button
from toggle_logic import toggle_specs


class DashboardHUD(ctk.CTkFrame):
    def __init__(self, master_app):
        super().__init__(master_app, fg_color="#0f1923")
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.is_revealed = False
        self.node_widgets = {}

        # 1. Title (Always visible)
        ctk.CTkLabel(self, text="V A L O P T", font=("Impact", 70),
                     text_color="#ff4655").pack(pady=(60, 20))

        # 2. Specs Grid Container
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        specs_factory.build_specs_grid(self.grid_container, self.node_widgets)

        # 3. HOME CONTROLS (Play, Reveal, Optimize)
        self.home_controls = ctk.CTkFrame(self, fg_color="transparent")
        self.home_controls.pack(expand=True)

        self.play_btn = ctk.CTkButton(
            self.home_controls, text="[ PLAY ]", font=("Arial", 22, "bold"),
            fg_color="transparent", border_color="#00ff7f", border_width=2,
            text_color="#00ff7f", height=70, width=300, command=self.handle_play_click
        )
        self.play_btn.pack(pady=20)

        self.home_footer = ctk.CTkFrame(
            self.home_controls, fg_color="transparent")
        self.home_footer.pack(pady=10)

        self.reveal_btn = ctk.CTkButton(
            self.home_footer, text="[ REVEAL SPECS ]", font=("Arial", 18),
            height=60, width=250, command=lambda: toggle_specs(self)
        )
        self.reveal_btn.pack(side="left", padx=20)

        self.optimize_btn = ctk.CTkButton(
            self.home_footer, text="[ OPTIMIZE ]", font=("Arial", 18),
            fg_color="#ff4655", height=60, width=250,
            command=self.show_optimize_menu  # New Function
        )
        self.optimize_btn.pack(side="left", padx=20)

        # 4. SPECS CONTROLS (Hide Specs)
        self.specs_controls = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkButton(
            self.specs_controls, text="[ HIDE SPECS ]", font=("Arial", 18),
            height=60, width=250, command=lambda: toggle_specs(self)
        ).pack(pady=40)

        # 5. OPTIMIZATION MENU (The Manual/Recommended View)
        self.opt_menu_container = ctk.CTkFrame(self, fg_color="transparent")
        # Note: Not packed yet

    def show_optimize_menu(self):
        """Hides home buttons and shows Manual/Recommended buttons."""
        self.home_controls.pack_forget()
        optimize_button.build_optimize_menu(self)

    def handle_play_click(self):
        self.play_btn.configure(text="[ LAUNCHING... ]", state="disabled")
        launcher.start_game(lambda: self.play_btn.configure(
            text="[ PLAY ]", state="normal"))
