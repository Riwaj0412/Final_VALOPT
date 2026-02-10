import customtkinter as ctk
import launcher
import specs_factory
import optimize_button
import styles
from toggle_logic import toggle_specs


class DashboardHUD(ctk.CTkFrame):
    def __init__(self, master_app):
        super().__init__(master_app, fg_color="#0f1923")
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.is_revealed = False
        self.node_widgets = {}

        # 1. Main Title
        ctk.CTkLabel(
            self, text="V A L O P T",
            font=styles.FONT_ORBITRON_LG,
            text_color="#ff4655"
        ).pack(pady=(60, 20))

        # 2. Specs Grid Container (Managed by toggle_logic)
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        specs_factory.build_specs_grid(self.grid_container, self.node_widgets)

        # 3. HOME CONTROLS (Main Menu)
        self.home_controls = ctk.CTkFrame(self, fg_color="transparent")
        self.home_controls.pack(expand=True)

        # LARGE PLAY BUTTON
        self.play_btn = ctk.CTkButton(
            self.home_controls, text="[ PLAY ]", font=styles.FONT_ORBITRON_MD,
            fg_color="transparent", border_color="#00ff7f", border_width=2,
            text_color="#00ff7f", height=90, width=450, command=self.handle_play_click
        )
        styles.apply_tactical_style(self.play_btn)
        self.play_btn.pack(pady=30)

        footer = ctk.CTkFrame(self.home_controls, fg_color="transparent")
        footer.pack(pady=10)

        # LARGE REVEAL BUTTON
        self.reveal_btn = ctk.CTkButton(
            footer, text="[ REVEAL SPECS ]", font=styles.FONT_ORBITRON_SM,
            fg_color="transparent", border_width=2, border_color="#3d799d",
            height=75, width=280, command=lambda: toggle_specs(self)
        )
        styles.apply_tactical_style(self.reveal_btn)
        self.reveal_btn.pack(side="left", padx=25)

        # LARGE OPTIMIZE BUTTON
        self.optimize_btn = ctk.CTkButton(
            footer, text="[ OPTIMIZE ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", height=75, width=280,
            command=self.show_optimize_menu
        )
        styles.apply_tactical_style(self.optimize_btn)
        self.optimize_btn.pack(side="left", padx=25)

        # 4. SPECS CONTROLS (Back to Home for revealed specs)
        self.specs_controls = ctk.CTkFrame(self, fg_color="transparent")
        self.back_home_btn = ctk.CTkButton(
            self.specs_controls, text="[ BACK TO HOME ]", font=styles.FONT_ORBITRON_SM,
            fg_color="transparent", border_width=2, border_color="#ff4655",
            text_color="#ff4655", height=60, width=300, command=lambda: toggle_specs(self)
        )
        styles.apply_tactical_style(self.back_home_btn)
        self.back_home_btn.pack(pady=40)

        self.opt_menu_container = ctk.CTkFrame(self, fg_color="transparent")

    def show_optimize_menu(self):
        self.home_controls.pack_forget()
        optimize_button.build_optimize_menu(self)

    def handle_play_click(self):
        self.play_btn.configure(text="[ LAUNCHING... ]", state="disabled")
        launcher.start_game(lambda: self.play_btn.configure(
            text="[ PLAY ]", state="normal"))
