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
        ctk.CTkLabel(
            self, text="FPS BENCHMARK",
            font=("Orbitron", 32, "bold"), text_color=_RED
        ).pack(pady=(28, 4))

        # RTSS status banner
        self._rtss_banner = ctk.CTkFrame(
            self, fg_color="#1a1a1a", corner_radius=8)
        self._rtss_banner.pack(fill="x", padx=60, pady=(0, 8))
        self._rtss_lbl = ctk.CTkLabel(
            self._rtss_banner, text="",
            font=("Orbitron", 11), text_color=_MUTED)
        self._rtss_lbl.pack(pady=8)
        self._refresh_rtss_banner()

        # live FPS
        self._live_lbl = ctk.CTkLabel(
            self, text="LIVE FPS  —",
            font=("Orbitron", 20, "bold"), text_color=_MUTED)
        self._live_lbl.pack(pady=(4, 12))

        # big button
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
        self._btn.pack(pady=6)

        self._status = ctk.CTkLabel(
            self,
            text="Press START while in a Valorant match.",
            font=("Orbitron", 13), text_color=_MUTED)
        self._status.pack(pady=(8, 4))

        # stats (shown after STOP)
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

    def _refresh_rtss_banner(self):
        if is_rtss_running():
            self._rtss_lbl.configure(
                text="✔  MSI Afterburner / RTSS detected  —  precise FPS active",
                text_color=_GREEN)
        else:
            self._rtss_lbl.configure(
                text="⚠  RTSS not detected  —  install MSI Afterburner for precise readings\n"
                     "Download: guru3d.com/download/msi-afterburner-beta-download",
                text_color=_YELLOW)

    def _on_back(self):
        self._live_on = False
        if self._recording:
            stop_capture()
            self._recording = False
        self._back_cmd()

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
            self._show_missing_tools_popup()
            return

        self._refresh_rtss_banner()
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

    def _show_results(self, result):
        if result.samples < 3:
            self._status.configure(
                text="⚠  Not enough data — play for at least 10 seconds before stopping.",
                text_color=_RED)
            return

        src_map = {"rtss": "RTSS / MSI Afterburner", "psutil": "Estimated"}
        src_txt = src_map.get(result.source, result.source)
        self._status.configure(
            text=f"{result.samples} samples  •  source: {src_txt}",
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
            card = ctk.CTkFrame(
                row, fg_color=_PANEL,
                corner_radius=10, width=118, height=108)
            card.pack_propagate(False)
            card.pack(side="left", padx=6)

            ctk.CTkLabel(
                card, text=f"{value:.0f}",
                font=("Orbitron", 28, "bold"), text_color=color
            ).pack(pady=(18, 2))

            ctk.CTkLabel(
                card, text=label,
                font=("Orbitron", 10), text_color=_MUTED
            ).pack()

        self._stats_frame.pack(pady=10)

    def _show_missing_tools_popup(self):
        import webbrowser

        popup = ctk.CTkToplevel(self)
        popup.title("VALOPT — Required Tool Missing")
        popup.geometry("500x340")
        popup.configure(fg_color=_DARK)
        popup.resizable(False, False)
        popup.grab_set()

        ctk.CTkLabel(
            popup, text="⚠  RTSS NOT RUNNING",
            font=("Orbitron", 17, "bold"), text_color=_RED
        ).pack(pady=(24, 6))

        ctk.CTkLabel(
            popup,
            text="FPS Benchmark requires RivaTuner Statistics Server (RTSS)\n"
                 "to read accurate frame data from Valorant.",
            font=("Orbitron", 11), text_color=_WHITE,
            justify="center"
        ).pack(pady=(0, 16))

        # download buttons
        links = [
            ("📥  MSI Afterburner (includes RTSS)",
             "https://www.msi.com/Landing/afterburner/graphics-cards",
             _RED),
            ("📥  RTSS Standalone (lighter)",
             "https://www.guru3d.com/download/rtss-rivatuner-statistics-server-download",
             _BLUE),
        ]

        for label, url, color in links:
            btn = ctk.CTkButton(
                popup, text=label,
                font=("Orbitron", 11, "bold"),
                fg_color=color,
                hover_color="#333333",
                text_color=_WHITE,
                height=40, width=380,
                corner_radius=6,
                command=lambda u=url: webbrowser.open(u)
            )
            btn.pack(pady=4)

        ctk.CTkLabel(
            popup,
            text="After installing, make sure RTSS is running in your\n"
                 "system tray, then press START again.",
            font=("Orbitron", 10), text_color=_MUTED,
            justify="center"
        ).pack(pady=(12, 4))

        ctk.CTkButton(
            popup, text="OK — I'll install it",
            font=("Orbitron", 12, "bold"),
            fg_color=_PANEL, hover_color="#2a2a2a",
            border_width=1, border_color="gray30",
            text_color=_WHITE, height=38, width=200,
            command=popup.destroy
        ).pack(pady=(4, 16))

    def _show_popup(self, title, msg):
        popup = ctk.CTkToplevel(self)
        popup.title("VALOPT")
        popup.geometry("420x180")
        popup.configure(fg_color=_DARK)
        popup.resizable(False, False)
        popup.grab_set()
        ctk.CTkLabel(popup, text=title,
                     font=("Orbitron", 15, "bold"), text_color=_RED
                     ).pack(pady=(28, 10))
        ctk.CTkLabel(popup, text=msg,
                     font=("Orbitron", 12), text_color=_WHITE
                     ).pack()
        ctk.CTkButton(popup, text="OK",
                      font=("Orbitron", 13, "bold"),
                      fg_color=_RED, hover_color="#ff5f6b",
                      text_color=_WHITE, height=40, width=120,
                      command=popup.destroy
                      ).pack(pady=16)
