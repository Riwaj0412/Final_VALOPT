import customtkinter as ctk
import styles
from manual_menu import ManualMenu


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
        content_frame,
        text="MANUAL",
        font=styles.FONT_IMPACT_LG,
        width=350,
        height=220,
        command=lambda: [
            [child.destroy()
             for child in dashboard.opt_menu_container.winfo_children()],
            ManualMenu(dashboard.opt_menu_container, lambda: build_optimize_menu(
                dashboard)).pack(fill="both", expand=True)
        ]
    )
    styles.apply_tactical_style(manual_btn)
    manual_btn.grid(row=0, column=0, padx=20)

    # --- THE GIANT SLASH ---
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
        dashboard.opt_menu_container,
        text="[ BACK TO HOME ]",
        font=("Arial", 16, "bold"),        # Increased size and made it bold
        fg_color="transparent",
        # Changed from TEXT_DIM to VALO_RED for high visibility
        text_color="#FF4655",
        hover_color="#2b2b2b",
        command=lambda: hide_optimize_menu(dashboard)
    )


# Reduced pady slightly to keep it on screen
    back_btn.pack(side="bottom", pady=40)


def hide_optimize_menu(dashboard):
    dashboard.opt_menu_container.pack_forget()
    dashboard.home_controls.pack(expand=True)
