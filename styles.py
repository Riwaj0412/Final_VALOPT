import customtkinter as ctk

# --- COLOR PALETTE ---
VALO_RED = "#ff4655"
VALO_DARK = "#0f1923"
VALO_GRAY = "#1a1a1a"
BORDER_COLOR = "#333333"
TEXT_MAIN = "#ffffff"
TEXT_DIM = "#808080"

# --- FONTS ---
FONT_IMPACT_LG = ("Impact", 45)
FONT_IMPACT_XL = ("Impact", 70)
# Made much bigger for that central split
FONT_SLASH = ("Arial", 180, "italic")
FONT_SANS_SM = ("Arial", 13, "bold")


def apply_tactical_style(button):
    """Applies the VALO-inspired HUD look to a button with hover effects."""
    button.configure(
        fg_color="transparent",
        text_color=TEXT_MAIN,
        border_color=BORDER_COLOR,
        border_width=2,
        # Hover color will change the background of the button
        hover_color=VALO_RED,  # Changes to VALO Red on hover
        corner_radius=5
    )
