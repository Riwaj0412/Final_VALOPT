import customtkinter as ctk
import styles


def build_optimize_menu(dashboard):
    """Creates the menu with a giant central slash and reactive buttons."""
    for widget in dashboard.opt_menu_container.winfo_children():
        widget.destroy()

    dashboard.opt_menu_container.pack(expand=True, fill="both")
    content_frame = ctk.CTkFrame(
        dashboard.opt_menu_container, fg_color="transparent")
    content_frame.pack(expand=True)

    # --- MANUAL BUTTON ---
    manual_btn = ctk.CTkButton(
        content_frame, text="MANUAL", font=styles.FONT_IMPACT_LG,
        width=350, height=220, command=lambda: print("Manual Mode")
    )
    styles.apply_tactical_style(manual_btn)
    manual_btn.grid(row=0, column=0, padx=20)

    # --- THE GIANT SLASH ---
    # Increased font size significantly as requested
    slash_label = ctk.CTkLabel(
        content_frame, text="/", font=styles.FONT_SLASH,
        text_color=styles.VALO_RED
    )
    slash_label.grid(row=0, column=1, padx=30)

    # --- RECOMMENDED BUTTON ---
    rec_btn = ctk.CTkButton(
        content_frame, text="RECOMMENDED", font=styles.FONT_IMPACT_LG,
        width=350, height=220, command=lambda: print("Recommended Mode")
    )
    styles.apply_tactical_style(rec_btn)
    rec_btn.grid(row=0, column=2, padx=20)

    # --- BACK BUTTON ---
    back_btn = ctk.CTkButton(
        dashboard.opt_menu_container, text="[ BACK TO HOME ]",
        font=styles.FONT_SANS_SM, fg_color="transparent",
        text_color=styles.TEXT_DIM, hover_color=styles.VALO_GRAY,
        command=lambda: hide_optimize_menu(dashboard)
    )
    back_btn.pack(side="bottom", pady=60)


def hide_optimize_menu(dashboard):
    dashboard.opt_menu_container.pack_forget()
    dashboard.home_controls.pack(expand=True)
