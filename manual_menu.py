import customtkinter as ctk
import styles
from tkinter import messagebox
from windows_menu import WindowsMenu
from ingame_menu import InGameMenu
from network_menu import NetworkMenu
import extreme_fps
import ram_cleaner
import priority
from session_logger import add_log


class ManualMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.back_command = back_command

        self.title_label = ctk.CTkLabel(
            self, text="MANUAL SETTINGS",
            font=styles.FONT_ORBITRON_MD,
            text_color="#ff4655"
        )
        self.title_label.pack(pady=(20, 10))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(expand=True, fill="both", padx=40)
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.create_grid_btn("IN-GAME", "#ff4655",
                             self.show_ingame_submenu, 0, 0)
        self.create_grid_btn("NVIDIA", "#76B900",
                             self.show_placeholder_msg, 0, 1)

        self.create_grid_btn("WINDOWS", "#808080",
                             self.show_windows_submenu, 1, 0)
        self.create_grid_btn("NETWORK", "#3d799d",
                             self.show_network_submenu, 1, 1)

        self.create_grid_btn("CLEAN RAM", "#3498db",
                             self.handle_ram_clean, 2, 0)
        self.create_grid_btn("EXTREME FPS", "#ff4655",
                             self.handle_extreme_fps, 2, 1, is_extreme=True)

        self.create_grid_btn("CPU PRIORITY", "#f39c12",
                             self.handle_cpu_prio, 3, 0)
        self.create_grid_btn("GPU PRIORITY", "#76B900",
                             self.handle_gpu_prio, 3, 1)

        self.hags_btn = ctk.CTkButton(
            self.button_frame, text="ENABLE HAGS (RESTART)",
            font=styles.FONT_ORBITRON_SM, height=60,
            fg_color="transparent", border_width=1, border_color="#9b59b6",
            command=self.handle_hags
        )
        styles.apply_tactical_style(self.hags_btn)
        self.hags_btn.grid(row=4, column=0, columnspan=2,
                           pady=10, padx=10, sticky="ew")

        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", hover_color="#ff5f6b",
            text_color="white", height=50, width=250,
            command=self.back_command
        )
        self.back_btn.pack(side="bottom", pady=20)

        self.current_submenu = None

    def create_grid_btn(self, text, color, cmd, row, col, is_extreme=False):
        txt_color = color if is_extreme else "white"
        btn = ctk.CTkButton(
            self.button_frame, text=text, font=styles.FONT_ORBITRON_SM,
            height=60, fg_color="transparent", border_width=1,
            border_color=color, text_color=txt_color, command=cmd
        )
        styles.apply_tactical_style(btn)
        btn.grid(row=row, column=col, pady=10, padx=10, sticky="ew")

    def handle_cpu_prio(self):
        success, msg = priority.set_cpu_high()
        if success:
            add_log(msg, status="SUCCESS")
            messagebox.showinfo("VALOPT", msg)
        else:
            messagebox.showwarning("VALOPT", msg)

    def handle_gpu_prio(self):
        success, msg = priority.set_gpu_high()
        if success:
            add_log(msg, status="SUCCESS")
            messagebox.showinfo("VALOPT", msg)
        else:
            messagebox.showerror("VALOPT", msg)

    def handle_hags(self):
        if messagebox.askyesno("VALOPT", "Enable HAGS? (Requires Restart)"):
            success, msg = priority.toggle_hags(True)
            if success:
                add_log(msg, status="SUCCESS")
                messagebox.showinfo("VALOPT", msg)
            else:
                messagebox.showerror("VALOPT", msg)

    def handle_ram_clean(self):
        amt = ram_cleaner.clean_memory()
        msg = f"RAM CLEANED: {amt}MB Released!" if amt > 0 else "RAM Optimized!"
        add_log(msg, status="SUCCESS")
        messagebox.showinfo("VALOPT", msg)

    def handle_extreme_fps(self):
        if messagebox.askyesno("VALOPT", "Apply EXTREME FPS settings?"):
            success, msg = extreme_fps.apply_extreme_optimizations()
            if success:
                add_log(msg, status="SUCCESS")
                messagebox.showinfo("VALOPT", msg)
            else:
                messagebox.showerror("VALOPT", msg)

    def show_placeholder_msg(self): messagebox.showinfo(
        "VALOPT", "Feature coming soon!")

    def show_ingame_submenu(self): self.hide_content(); self.current_submenu = InGameMenu(
        self, self.restore_menu); self.current_submenu.pack(fill="both", expand=True)

    def show_windows_submenu(self): self.hide_content(); self.current_submenu = WindowsMenu(
        self, self.restore_menu); self.current_submenu.pack(fill="both", expand=True)
    def show_network_submenu(self): self.hide_content(); self.current_submenu = NetworkMenu(
        self, self.restore_menu); self.current_submenu.pack(fill="both", expand=True)

    def hide_content(self): self.title_label.pack_forget(
    ); self.button_frame.pack_forget(); self.back_btn.pack_forget()

    def restore_menu(self):
        if self.current_submenu:
            self.current_submenu.destroy()
        self.title_label.pack(pady=(20, 10))
        self.button_frame.pack(expand=True, fill="both", padx=40)
        self.back_btn.pack(side="bottom", pady=20)
