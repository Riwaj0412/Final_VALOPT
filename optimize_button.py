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
        selection_frame, text="MANUAL", font=styles.FONT_ORBITRON_MD,
        width=380, height=250, fg_color="transparent", border_width=1, border_color="gray30",
        command=lambda: show_manual(dashboard, selection_frame)
    )
    styles.apply_tactical_style(manual_btn)
    manual_btn.pack(side="left", padx=20)

    # --- DECORATIVE SLASH ---
    ctk.CTkLabel(selection_frame, text="/", font=("Impact", 120),
                 text_color="#ff4655").pack(side="left", padx=15)

    # --- RECOMMENDED BUTTON ---
    rec_btn = ctk.CTkButton(
        selection_frame, text="RECOMMENDED", font=styles.FONT_ORBITRON_MD,
        width=380, height=250, fg_color="transparent", border_width=1, border_color="gray30",
        command=lambda: print("Recommended logic...")
    )
    styles.apply_tactical_style(rec_btn)
    rec_btn.pack(side="left", padx=20)

    # --- BACK TO HOME BUTTON ---
    back_home = ctk.CTkLabel(
        dashboard.opt_menu_container, text="[ BACK TO HOME ]",
        font=styles.FONT_ORBITRON_SM, text_color="#ff4655", cursor="hand2"
    )
    back_home.pack(side="bottom", pady=40)
    back_home.bind("<Button-1>", lambda e: return_to_home(dashboard))


def show_manual(dashboard, selection_frame):
    selection_frame.pack_forget()
    # Hides the back label before showing sub-menu
    for child in dashboard.opt_menu_container.winfo_children():
        if isinstance(child, ctk.CTkLabel) and child.cget("text") == "[ BACK TO HOME ]":
            child.pack_forget()

    m_menu = ManualMenu(dashboard.opt_menu_container,
                        lambda: build_optimize_menu(dashboard))
    m_menu.pack(fill="both", expand=True)


def return_to_home(dashboard):
    dashboard.opt_menu_container.pack_forget()
    dashboard.home_controls.pack(expand=True)
