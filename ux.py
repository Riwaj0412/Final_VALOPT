import customtkinter as ctk
import os
from ctypes import windll

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")

try:
    font_path = os.path.join(ASSETS_PATH, "Orbitron-Regular.ttf")
    windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
except:
    pass


def get_font(size):
    return ("Orbitron", size, "bold")


def center_window(window, width, height):
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    x = (sw // 2) - (width // 2)
    y = (sh // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


class SpecNode(ctk.CTkFrame):
    def __init__(self, master, title, icon, value, **kwargs):
        super().__init__(master, fg_color="#0a0a0a", border_color="#ff4655",
                         border_width=2, corner_radius=12, **kwargs)

        ctk.CTkLabel(self, text=icon, font=(
            "Segoe UI Symbol", 35)).pack(pady=(20, 5))

        ctk.CTkLabel(self, text=title, font=get_font(20),
                     text_color="#ff4655").pack()

        self.val_label = ctk.CTkLabel(self, text=str(value), font=("Consolas", 18),
                                      text_color="white", wraplength=350)
        self.val_label.pack(pady=(5, 20))

    def update_value(self, new_value):
        self.val_label.configure(text=str(new_value))
