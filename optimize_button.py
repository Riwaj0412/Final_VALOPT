import customtkinter as ctk
import styles
import threading
from manual_menu import ManualMenu
from recommended import apply_recommended_optimizations


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
        font=("Orbitron", 50, "bold"),
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
        font=("Orbitron", 50, "bold"),
        width=380,
        height=250,
        fg_color="transparent",
        border_width=1,
        border_color="gray30",
        command=lambda: run_recommended(dashboard)
    )
    styles.apply_tactical_style(rec_btn)
    rec_btn.pack(side="left", padx=20)

    # --- UNIFIED BACK TO HOME BUTTON ---
    back_home_btn = ctk.CTkButton(
        dashboard.opt_menu_container,
        text="BACK",
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


def _find_btn_by_text(dashboard, text):
    for child in dashboard.opt_menu_container.winfo_children():
        for widget in getattr(child, 'winfo_children', lambda: [])():
            if isinstance(widget, ctk.CTkButton):
                try:
                    if widget.cget("text") == text:
                        return widget
                except Exception:
                    pass
    return None


def run_recommended(dashboard):
    btn = _find_btn_by_text(dashboard, "RECOMMENDED")
    if btn:
        btn.configure(text="OPTIMIZING...",
                      state="disabled", fg_color="#ff4655")

    def _worker():
        results = apply_recommended_optimizations()
        dashboard.after(0, lambda: _show_results(dashboard, results))

    threading.Thread(target=_worker, daemon=True).start()


def _show_results(dashboard, results):
    btn = _find_btn_by_text(dashboard, "OPTIMIZING...")
    if btn:
        btn.configure(text="RECOMMENDED", state="normal",
                      fg_color="transparent")
        styles.apply_tactical_style(btn)

    # Build result window
    popup = ctk.CTkToplevel(dashboard)
    popup.title("VALOPT — Optimization Results")
    popup.geometry("520x480")
    popup.configure(fg_color="#0f0f0f")
    popup.resizable(False, False)
    popup.grab_set()

    ctk.CTkLabel(
        popup, text="OPTIMIZATION COMPLETE",
        font=("Orbitron", 18, "bold"), text_color="#ff4655"
    ).pack(pady=(24, 12))

    scroll = ctk.CTkScrollableFrame(popup, fg_color="#1a1a1a", corner_radius=8)
    scroll.pack(fill="both", expand=True, padx=20, pady=(0, 12))

    passed = 0
    for label, ok in results:
        icon = "✔" if ok else "⚠"
        color = "#00e676" if ok else "#ff9800"
        row = ctk.CTkFrame(scroll, fg_color="transparent")
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text=icon,  font=("Orbitron", 13, "bold"),
                     text_color=color, width=28).pack(side="left")
        ctk.CTkLabel(row, text=label, font=("Orbitron", 11),
                     text_color="white", anchor="w").pack(side="left", padx=6)
        if ok:
            passed += 1

    summary = f"{passed}/{len(results)} optimizations applied"
    ctk.CTkLabel(
        popup, text=summary,
        font=("Orbitron", 12), text_color="gray60"
    ).pack(pady=(0, 8))

    ctk.CTkButton(
        popup, text="CLOSE",
        font=("Orbitron", 13, "bold"),
        fg_color="#ff4655", hover_color="#ff5f6b",
        text_color="white", height=44, width=200, corner_radius=4,
        command=popup.destroy
    ).pack(pady=(0, 20))


def show_manual_menu(dashboard, selection_frame):
    selection_frame.pack_forget()

    for child in dashboard.opt_menu_container.winfo_children():
        if isinstance(child, ctk.CTkButton) and child.cget("text") == "BACK":
            child.pack_forget()

    m_menu = ManualMenu(dashboard.opt_menu_container,
                        lambda: build_optimize_menu(dashboard))
    m_menu.pack(fill="both", expand=True)


def return_to_dashboard(dashboard):
    dashboard.show_home()
