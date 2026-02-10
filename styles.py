import customtkinter as ctk
import os

FONT_PATH = os.path.join(os.path.dirname(
    __file__), "assets", "Orbitron-Regular.ttf")
# --- COLOR PALETTE ---
VALO_RED = "#ff4655"
VALO_DARK = "#0f1923"
VALO_GRAY = "#1a1a1a"
BORDER_COLOR = "#333333"
TEXT_MAIN = "#ffffff"
TEXT_DIM = "#808080"


if os.path.exists(FONT_PATH):
    ctk.FontManager.load_font(FONT_PATH)
    FONT_ORBITRON_LG = ("Orbitron", 80)
    FONT_ORBITRON_MD = ("Orbitron", 28, "bold")
    FONT_ORBITRON_SM = ("Orbitron", 20)
else:
    # Fallback so the app doesn't crash if the file is moved
    FONT_ORBITRON_LG = ("Impact", 80)
    FONT_ORBITRON_MD = ("Arial", 28, "bold")
    FONT_ORBITRON_SM = ("Arial", 20)


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
    button.configure(hover_color="#ff4655")
