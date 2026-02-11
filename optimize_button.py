import customtkinter as ctk
import styles
# Essential to prevent "Undefined Variable" error
from manual_menu import ManualMenu


def build_optimize_menu(dashboard):
    # Clear any previous content from the container
    for child in dashboard.opt_menu_container.winfo_children():
        child.destroy()

    dashboard.opt_menu_container.pack(fill="both", expand=True)

    # Main horizontal layout frame for the two options
    selection_frame = ctk.CTkFrame(
        dashboard.opt_menu_container, fg_color="transparent")
    selection_frame.pack(expand=True)

    # --- MANUAL BUTTON ---
    manual_btn = ctk.CTkButton(
        selection_frame,
        text="MANUAL",
        font=styles.FONT_ORBITRON_MD,  # Corrected Orbitron font
        width=380,
        height=250,
        fg_color="transparent",
        border_width=1,
        border_color="gray30",
        command=lambda: show_manual_menu(dashboard, selection_frame)
    )
    styles.apply_tactical_style(manual_btn)
    manual_btn.pack(side="left", padx=20)

    # --- THE SLASH (/) DECORATION ---
    ctk.CTkLabel(
        selection_frame,
        text="/",
        font=("Impact", 120),
        text_color="#ff4655"
    ).pack(side="left", padx=15)

    # --- RECOMMENDED BUTTON ---
    rec_btn = ctk.CTkButton(
        selection_frame,
        text="RECOMMENDED",
        font=styles.FONT_ORBITRON_MD,
        width=380,
        height=250,
        fg_color="transparent",
        border_width=1,
        border_color="gray30",
        command=lambda: print("Applying Recommended Optimizations...")
    )
    styles.apply_tactical_style(rec_btn)
    rec_btn.pack(side="left", padx=20)

    # --- UNIFIED BACK TO HOME BUTTON ---
    # Now using a CTkButton with a solid red background to match Specs view
    back_home_btn = ctk.CTkButton(
        dashboard.opt_menu_container,
        text="[ BACK TO HOME ]",
        font=styles.FONT_ORBITRON_SM,
        fg_color="#ff4655",         # Solid red background
        hover_color="#ff5f6b",      # Slightly lighter red on hover
        text_color="white",
        height=60,
        width=300,
        corner_radius=4,
        command=lambda: return_to_dashboard(dashboard)
    )
    back_home_btn.pack(side="bottom", pady=40)


def show_manual_menu(dashboard, selection_frame):
    """Hides selection and launches the manual sub-menu"""
    selection_frame.pack_forget()

    # Locate and hide the solid red back button before loading ManualMenu
    for child in dashboard.opt_menu_container.winfo_children():
        if isinstance(child, ctk.CTkButton) and child.cget("text") == "[ BACK TO HOME ]":
            child.pack_forget()

    # Launch ManualMenu and provide the command to return to this Optimize page
    m_menu = ManualMenu(dashboard.opt_menu_container,
                        lambda: build_optimize_menu(dashboard))
    m_menu.pack(fill="both", expand=True)


def return_to_dashboard(dashboard):
    """Returns to the main dashboard screen"""
    dashboard.opt_menu_container.pack_forget()
    dashboard.home_controls.pack(expand=True)
