import customtkinter as ctk
import threading
import styles

from fps_reader import (is_valorant_running, is_rtss_running,
                        start_capture, stop_capture, get_live_fps)

_RED = "#ff4655"
_DARK = "#0f0f0f"
_PANEL = "#1a1a1a"
_MUTED = "#555555"
_WHITE = "#ffffff"
_GREEN = "#00c853"
_ORANGE = "#ff9800"
_BLUE = "#2979ff"
_YELLOW = "#ffd600"


class BenchmarkMenu(ctk.CTkFrame):
    def __init__(self, master, back_cmd):
        super().__init__(master, fg_color="transparent")
        self._back_cmd = back_cmd
        self._recording = False
        self._live_on = True

        # title
        ctk.CTkLabel(self, text="FPS BENCHMARK",
                     font=("Orbitron", 32, "bold"),
                     text_color=_RED).pack(pady=(28, 4))

        # RTSS status
        self._rtss_lbl = ctk.CTkLabel(
            self, text="",
            font=("Orbitron", 11), text_color=_MUTED)
        self._rtss_lbl.pack(pady=(0, 4))
        self._refresh_rtss()

        # live fps
        self._live_lbl = ctk.CTkLabel(
            self, text="LIVE FPS  —",
            font=("Orbitron", 20, "bold"), text_color=_MUTED)
        self._live_lbl.pack(pady=(4, 10))

        # big button
        self._btn = ctk.CTkButton(
            self, text="START",
            font=("Orbitron", 52, "bold"),
            width=340, height=160,
            corner_radius=12,
            fg_color=_GREEN, hover_color="#00a846",
            text_color=_WHITE,
            command=self._toggle)
        self._btn.pack(pady=6)

        self._status = ctk.CTkLabel(
            self,
            text="Press START while in a Valorant match.",
            font=("Orbitron", 13), text_color=_MUTED)
        self._status.pack(pady=(8, 4))

        # stats frame — shown after stop
        self._stats_frame = ctk.CTkFrame(self, fg_color="transparent")

        # back
        ctk.CTkButton(
            self, text="[ BACK ]",
            font=styles.FONT_ORBITRON_SM,
            fg_color=_RED, hover_color="#ff5f6b",
            text_color=_WHITE, height=56, width=300,
            command=self._on_back
        ).pack(side="bottom", pady=26)

        self._update_live()

    # ── RTSS badge ────────────────────────────────────────────────────────────
    def _refresh_rtss(self):
        if is_rtss_running():
            self._rtss_lbl.configure(
                text="✔  RTSS detected — precise FPS",
                text_color=_GREEN)
        else:
            self._rtss_lbl.configure(
                text="⚠  RTSS not running — install MSI Afterburner for best accuracy",
                text_color=_YELLOW)

    # ── back ──────────────────────────────────────────────────────────────────
    def _on_back(self):
        self._live_on = False
        if self._recording:
            stop_capture()
            self._recording = False
        self._back_cmd()

    # ── live ticker ───────────────────────────────────────────────────────────
    def _update_live(self):
        if not self._live_on:
            return
        fps = get_live_fps()
        if fps and self._recording:
            self._live_lbl.configure(
                text=f"LIVE FPS  {fps:.0f}", text_color=_ORANGE)
        else:
            self._live_lbl.configure(text="LIVE FPS  —", text_color=_MUTED)
        self.after(300, self._update_live)

    # ── toggle ────────────────────────────────────────────────────────────────
    def _toggle(self):
        if not self._recording:
            self._do_start()
        else:
            self._do_stop()

    def _do_start(self):
        if not is_valorant_running():
            self._show_popup(
                "⚠  VALORANT IS NOT RUNNING",
                "Open Valorant and load into a match first.")
            return

        if not is_rtss_running():
            self._show_missing_rtss_popup()
            return

        self._refresh_rtss()
        self._recording = True
        self._btn.configure(text="STOP", fg_color=_RED, hover_color="#cc2233")
        self._status.configure(
            text="● Recording — play normally, then press STOP.",
            text_color=_RED)
        self._stats_frame.pack_forget()
        start_capture()

    def _do_stop(self):
        self._recording = False
        self._btn.configure(text="START", fg_color=_GREEN,
                            hover_color="#00a846")
        self._status.configure(text="Calculating…", text_color=_ORANGE)
        self._live_lbl.configure(text="LIVE FPS  —", text_color=_MUTED)
        threading.Thread(target=self._finish, daemon=True).start()

    def _finish(self):
        result = stop_capture()
        self.after(0, lambda: self._show_results(result))

    # ── results ───────────────────────────────────────────────────────────────
    def _show_results(self, result):
        if result.samples < 5:
            self._status.configure(
                text="⚠  Not enough data — play for at least 10 seconds.",
                text_color=_RED)
            return

        src_map = {"rtss": "RTSS", "psutil": "Estimated"}
        self._status.configure(
            text=f"{result.samples} samples  •  source: {src_map.get(result.source, result.source)}",
            text_color=_MUTED)

        for w in self._stats_frame.winfo_children():
            w.destroy()

        stats = [
            ("AVG",    result.avg,  _WHITE),
            ("MAX",    result.max,  _GREEN),
            ("MIN",    result.min,  _RED),
            ("1% LOW", result.low1, _ORANGE),
            ("99th%",  result.p99,  _BLUE),
        ]

        row = ctk.CTkFrame(self._stats_frame, fg_color="transparent")
        row.pack()

        for label, value, color in stats:
            card = ctk.CTkFrame(row, fg_color=_PANEL,
                                corner_radius=10, width=118, height=108)
            card.pack_propagate(False)
            card.pack(side="left", padx=6)

            ctk.CTkLabel(card, text=f"{value:.0f}",
                         font=("Orbitron", 28, "bold"),
                         text_color=color).pack(pady=(18, 2))
            ctk.CTkLabel(card, text=label,
                         font=("Orbitron", 10),
                         text_color=_MUTED).pack()

        self._stats_frame.pack(pady=10)

    # ── RTSS missing popup ────────────────────────────────────────────────────
    def _show_missing_rtss_popup(self):
        import webbrowser
        popup = ctk.CTkToplevel(self)
        popup.title("VALOPT")
        popup.geometry("500x300")
        popup.configure(fg_color=_DARK)
        popup.resizable(False, False)
        popup.grab_set()

        ctk.CTkLabel(popup, text="⚠  RTSS NOT RUNNING",
                     font=("Orbitron", 16, "bold"),
                     text_color=_RED).pack(pady=(24, 8))
        ctk.CTkLabel(popup,
                     text="FPS Benchmark needs RivaTuner Statistics Server.\nInstall it then make sure it's running in the system tray.",
                     font=("Orbitron", 11), text_color=_WHITE,
                     justify="center").pack(pady=(0, 14))

        for label, url in [
            ("📥  MSI Afterburner (recommended)",
             "https://www.msi.com/Landing/afterburner/graphics-cards"),
            ("📥  RTSS Standalone",
             "https://www.guru3d.com/download/rtss-rivatuner-statistics-server-download"),
        ]:
            ctk.CTkButton(popup, text=label,
                          font=("Orbitron", 11, "bold"),
                          fg_color=_PANEL, hover_color="#2a2a2a",
                          border_width=1, border_color=_RED,
                          text_color=_WHITE, height=38, width=380,
                          command=lambda u=url: webbrowser.open(u)
                          ).pack(pady=3)

        ctk.CTkButton(popup, text="OK", font=("Orbitron", 12, "bold"),
                      fg_color=_RED, hover_color="#ff5f6b",
                      text_color=_WHITE, height=38, width=160,
                      command=popup.destroy).pack(pady=(12, 0))

    # ── generic popup ─────────────────────────────────────────────────────────
    def _show_popup(self, title, msg):
        popup = ctk.CTkToplevel(self)
        popup.title("VALOPT")
        popup.geometry("420x175")
        popup.configure(fg_color=_DARK)
        popup.resizable(False, False)
        popup.grab_set()
        ctk.CTkLabel(popup, text=title,
                     font=("Orbitron", 15, "bold"),
                     text_color=_RED).pack(pady=(28, 10))
        ctk.CTkLabel(popup, text=msg,
                     font=("Orbitron", 12),
                     text_color=_WHITE).pack()
        ctk.CTkButton(popup, text="OK",
                      font=("Orbitron", 13, "bold"),
                      fg_color=_RED, hover_color="#ff5f6b",
                      text_color=_WHITE, height=40, width=120,
                      command=popup.destroy).pack(pady=16)
