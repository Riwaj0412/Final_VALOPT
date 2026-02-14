import customtkinter as ctk
import styles
from manual_menu import ManualMenu


def build_optimize_menu(dashboard):
    for child in dashboard.opt_menu_container.winfo_children():
        child.destroy()

    dashboard.opt_menu_container.pack(fill="both", expand=True)

    selection_frame = ctk.CTkFrame(
        dashboard.opt_menu_container, fg_color="transparent")
    selection_frame.pack(expand=True)

    # --- MANUAL BUTTON ---
    manual_btn = ctk.CTkButton(
        selection_frame,
        text="MANUAL",
        font=styles.FONT_ORBITRON_MD,
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
    back_home_btn = ctk.CTkButton(
        dashboard.opt_menu_container,
        text="[ BACK ]",
        font=styles.FONT_ORBITRON_SM,
        fg_color="#ff4655",
        hover_color="#ff5f6b",
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

    for child in dashboard.opt_menu_container.winfo_children():
        if isinstance(child, ctk.CTkButton) and child.cget("text") == "[ BACK ]":
            child.pack_forget()

    m_menu = ManualMenu(dashboard.opt_menu_container,
                        lambda: build_optimize_menu(dashboard))
    m_menu.pack(fill="both", expand=True)


def return_to_dashboard(dashboard):
    """Returns to the main dashboard screen"""
    dashboard.opt_menu_container.pack_forget()
    dashboard.home_controls.pack(expand=True)
