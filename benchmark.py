import customtkinter as ctk
import threading
import styles

from fps_reader import (is_valorant_running, start_capture,
                        stop_capture, get_live_fps)


_RED = "#ff4655"
_DARK = "#0f0f0f"
_PANEL = "#1a1a1a"
_MUTED = "#555555"
_WHITE = "#ffffff"
_GREEN = "#00c853"
_ORANGE = "#ff9800"
_BLUE = "#2979ff"


class BenchmarkMenu(ctk.CTkFrame):
    def __init__(self, master, back_cmd):
        super().__init__(master, fg_color="transparent")
        self._back_cmd = back_cmd
        self._recording = False
        self._live_on = True

        # title
        ctk.CTkLabel(
            self, text="FPS BENCHMARK",
            font=("Orbitron", 32, "bold"), text_color=_RED
        ).pack(pady=(30, 4))

        ctk.CTkLabel(
            self,
            text="Non-invasive sampling  —  zero game impact",
            font=("Orbitron", 11), text_color=_MUTED
        ).pack(pady=(0, 4))

        # live ticker
        self._live_lbl = ctk.CTkLabel(
            self, text="LIVE FPS  —",
            font=("Orbitron", 20, "bold"), text_color=_MUTED)
        self._live_lbl.pack(pady=(4, 16))

        # big START / STOP button
        self._btn = ctk.CTkButton(
            self,
            text="START",
            font=("Orbitron", 52, "bold"),
            width=340, height=160,
            corner_radius=12,
            fg_color=_GREEN,
            hover_color="#00a846",
            text_color=_WHITE,
            command=self._toggle
        )
        self._btn.pack(pady=8)

        self._status = ctk.CTkLabel(
            self,
            text="Press START while in a Valorant match.",
            font=("Orbitron", 13), text_color=_MUTED)
        self._status.pack(pady=(8, 4))

        # stats frame — shown after first STOP
        self._stats_frame = ctk.CTkFrame(self, fg_color="transparent")

        # back
        ctk.CTkButton(
            self, text="[ BACK ]",
            font=styles.FONT_ORBITRON_SM,
            fg_color=_RED, hover_color="#ff5f6b",
            text_color=_WHITE, height=56, width=300,
            command=self._on_back
        ).pack(side="bottom", pady=28)

        self._update_live()

    # ── back ───────────────────────────────────────────────────────────────────
    def _on_back(self):
        self._live_on = False
        if self._recording:
            stop_capture()
            self._recording = False
        self._back_cmd()

    # ── live ticker ─────────────────────────────────────────────────────────────
    def _update_live(self):
        if not self._live_on:
            return
        fps = get_live_fps()
        if fps and self._recording:
            self._live_lbl.configure(
                text=f"LIVE FPS  {fps:.0f}", text_color=_ORANGE)
        else:
            self._live_lbl.configure(
                text="LIVE FPS  —", text_color=_MUTED)
        self.after(400, self._update_live)

    # ── toggle ──────────────────────────────────────────────────────────────────
    def _toggle(self):
        if not self._recording:
            self._do_start()
        else:
            self._do_stop()

    def _do_start(self):
        if not is_valorant_running():
            self._show_no_game_popup()
            return

        self._recording = True
        self._btn.configure(
            text="STOP",
            fg_color=_RED,
            hover_color="#cc2233")
        self._status.configure(
            text="● Recording — play normally, then press STOP.",
            text_color=_RED)
        self._stats_frame.pack_forget()
        start_capture()

    def _do_stop(self):
        self._recording = False
        self._btn.configure(
            text="START",
            fg_color=_GREEN,
            hover_color="#00a846")
        self._status.configure(
            text="Calculating results…", text_color=_ORANGE)
        self._live_lbl.configure(text="LIVE FPS  —", text_color=_MUTED)
        threading.Thread(target=self._finish, daemon=True).start()

    def _finish(self):
        result = stop_capture()
        self.after(0, lambda: self._show_results(result))

    # ── results ─────────────────────────────────────────────────────────────────
    def _show_results(self, result):
        if result.samples < 2:
            self._status.configure(
                text="⚠  Not enough data — play longer before stopping.",
                text_color=_RED)
            return

        self._status.configure(
            text=f"Complete — {result.samples} samples captured",
            text_color=_MUTED)

        for w in self._stats_frame.winfo_children():
            w.destroy()

        stats = [
            ("AVG",     result.avg,  _WHITE),
            ("MAX",     result.max,  _GREEN),
            ("MIN",     result.min,  _RED),
            ("1% LOW",  result.low1, _ORANGE),
            ("99th%",   result.p99,  _BLUE),
        ]

        row = ctk.CTkFrame(self._stats_frame, fg_color="transparent")
        row.pack()

        for label, value, color in stats:
            card = ctk.CTkFrame(
                row, fg_color=_PANEL,
                corner_radius=10, width=118, height=108)
            card.pack_propagate(False)
            card.pack(side="left", padx=6)

            ctk.CTkLabel(
                card, text=f"{value:.0f}",
                font=("Orbitron", 30, "bold"), text_color=color
            ).pack(pady=(18, 2))

            ctk.CTkLabel(
                card, text=label,
                font=("Orbitron", 10), text_color=_MUTED
            ).pack()

        self._stats_frame.pack(pady=10)

    # ── no game popup ────────────────────────────────────────────────────────────
    def _show_no_game_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("VALOPT")
        popup.geometry("400x170")
        popup.configure(fg_color=_DARK)
        popup.resizable(False, False)
        popup.grab_set()

        ctk.CTkLabel(
            popup, text="⚠  VALORANT IS NOT RUNNING",
            font=("Orbitron", 16, "bold"), text_color=_RED
        ).pack(pady=(28, 10))

        ctk.CTkLabel(
            popup, text="Open Valorant and load into a match first.",
            font=("Orbitron", 12), text_color=_WHITE
        ).pack()

        ctk.CTkButton(
            popup, text="OK",
            font=("Orbitron", 13, "bold"),
            fg_color=_RED, hover_color="#ff5f6b",
            text_color=_WHITE, height=40, width=120,
            command=popup.destroy
        ).pack(pady=18)
