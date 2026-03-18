import customtkinter as ctk
import psutil
import threading
import time
import os
import styles

try:
    import GPUtil
    _GPUTIL = True
except ImportError:
    _GPUTIL = False

from tkinter import filedialog

from fps_reader import (is_valorant_running, find_presentmon, detect_source,
                        start_capture, stop_capture,
                        get_live_fps, parse_capframex_file)
from benchmark_data import (save_before, save_after,
                            load as load_benchmark, clear as clear_benchmark)

_RED = "#ff4655"
_DARK = "#0f0f0f"
_PANEL = "#1a1a1a"
_PANEL2 = "#222222"
_MUTED = "#666666"
_WHITE = "#ffffff"
_GREEN = "#00e676"
_ORANGE = "#ff9800"
_BLUE = "#2979ff"

_FH = ("Orbitron", 26, "bold")
_FM = ("Orbitron", 17, "bold")
_FS = ("Orbitron", 14)
_FT = ("Orbitron", 13)
_FX = ("Orbitron", 11)

_SRC_COLOUR = {
    "presentmon": _GREEN,
    "capframex":  _BLUE,
    "psutil":     _ORANGE,
    "none":       _MUTED,
    "no_data":    _RED,
}
_SRC_LABEL = {
    "presentmon": "📡 PresentMon (precise)",
    "capframex":  "📊 CapFrameX",
    "psutil":     "⚙ Estimated (psutil)",
    "none":       "— No source detected",
    "no_data":    "⚠ No data captured",
}


class BenchmarkMenu(ctk.CTkFrame):
    def __init__(self, master, back_cmd):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(self, text="BENCHMARK & MONITOR",
                     font=_FH, text_color=_RED).pack(pady=(24, 8))

        tab_bar = ctk.CTkFrame(self, fg_color=_PANEL, corner_radius=8)
        tab_bar.pack(fill="x", padx=30, pady=(0, 8))
        self._tab_btns = {}
        self._tab_frames = {}
        for name in ("LIVE", "FPS BENCHMARK", "COMPARISON"):
            btn = ctk.CTkButton(
                tab_bar, text=name, font=_FX,
                fg_color="transparent", hover_color="#2a2a2a",
                text_color=_WHITE, height=36, corner_radius=6,
                command=lambda n=name: self._switch_tab(n))
            btn.pack(side="left", padx=4, pady=4)
            self._tab_btns[name] = btn

        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=30)

        self._build_live_tab()
        self._build_benchmark_tab()
        self._build_comparison_tab()
        self._switch_tab("LIVE")

        ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color=_RED, hover_color="#ff5f6b",
            height=60, width=320, command=self._on_back(back_cmd)
        ).pack(side="bottom", pady=24)

        self._live_running = True
        self._recording_mode = None
        self._update_live()
        self._watch_for_game()

    def _on_back(self, back_cmd):
        def _inner():
            self._live_running = False
            if self._recording_mode:
                stop_capture()
                self._recording_mode = None
            back_cmd()
        return _inner

    def _switch_tab(self, name: str):
        for f in self._tab_frames.values():
            f.pack_forget()
        self._tab_frames[name].pack(fill="both", expand=True)
        for n, b in self._tab_btns.items():
            b.configure(fg_color=_RED if n == name else "transparent")
        if name == "COMPARISON":
            self._refresh_comparison()

    def _build_live_tab(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        self._tab_frames["LIVE"] = f
        stats = ctk.CTkFrame(f, fg_color="transparent")
        stats.pack(expand=True, pady=20)

        def stat(text, color=_WHITE):
            l = ctk.CTkLabel(stats, text=text,
                             font=("Orbitron", 24, "bold"), text_color=color)
            l.pack(pady=12)
            return l

        self._cpu_lbl = stat("CPU USAGE: --%")
        self._gpu_lbl = stat("GPU USAGE: --%")
        self._ram_lbl = stat("RAM USAGE: --%")
        self._fps_live = stat("LIVE FPS: --", _ORANGE)
        self._src_live = ctk.CTkLabel(
            stats, text="", font=_FX, text_color=_MUTED)
        self._src_live.pack()

    def _update_live(self):
        if not self._live_running:
            return
        self._cpu_lbl.configure(text=f"CPU USAGE: {psutil.cpu_percent():.1f}%")
        self._ram_lbl.configure(
            text=f"RAM USAGE: {psutil.virtual_memory().percent:.1f}%")

        gpu_text = "GPU: N/A"
        if _GPUTIL:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_text = f"GPU: {gpus[0].load*100:.1f}%  TEMP: {gpus[0].temperature}°C"
            except Exception:
                pass
        self._gpu_lbl.configure(text=gpu_text)

        live = get_live_fps()
        self._fps_live.configure(
            text=f"LIVE FPS: {live:.0f}" if live else "LIVE FPS: (start recording)")

        src = detect_source()
        self._src_live.configure(
            text=f"Source: {_SRC_LABEL.get(src, src)}",
            text_color=_SRC_COLOUR.get(src, _MUTED))

        self.after(1000, self._update_live)

    def _build_benchmark_tab(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        self._tab_frames["FPS BENCHMARK"] = f

        # status
        self._bench_status = ctk.CTkLabel(
            f, text="Press RECORD BEFORE, play for a while, then press STOP.",
            font=_FS, text_color=_MUTED, wraplength=640)
        self._bench_status.pack(pady=(14, 2))

        # source + setup tip
        self._src_badge = ctk.CTkLabel(f, text="", font=_FX, text_color=_MUTED)
        self._src_badge.pack()
        self._pm_tip = ctk.CTkLabel(f, text="", font=_FX,
                                    text_color=_ORANGE, wraplength=640)
        self._pm_tip.pack(pady=(0, 6))
        self._refresh_src_badge()

        # cards
        cards = ctk.CTkFrame(f, fg_color="transparent")
        cards.pack(pady=8)
        self._before_card = self._make_fps_card(cards, "BEFORE", _RED)
        self._before_card.pack(side="left", padx=14)
        self._after_card = self._make_fps_card(cards, "AFTER",  _GREEN)
        self._after_card.pack(side="left", padx=14)

        # main buttons
        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(pady=10)

        self._btn_before = ctk.CTkButton(
            btn_row, text="⏺  RECORD BEFORE", font=_FT,
            fg_color=_PANEL, hover_color=_PANEL2,
            border_width=1, border_color=_RED,
            text_color=_WHITE, height=46, width=210,
            command=lambda: self._start_recording("before"))
        self._btn_before.pack(side="left", padx=8)

        self._btn_after = ctk.CTkButton(
            btn_row, text="⏺  RECORD AFTER", font=_FT,
            fg_color=_PANEL, hover_color=_PANEL2,
            border_width=1, border_color=_GREEN,
            text_color=_WHITE, height=46, width=210,
            command=lambda: self._start_recording("after"))
        self._btn_after.pack(side="left", padx=8)

        self._btn_stop = ctk.CTkButton(
            btn_row, text="⏹  STOP", font=_FT,
            fg_color=_RED, hover_color="#ff5f6b",
            text_color=_WHITE, height=46, width=120,
            command=self._stop_recording, state="disabled")
        self._btn_stop.pack(side="left", padx=8)

        # secondary row
        sec = ctk.CTkFrame(f, fg_color="transparent")
        sec.pack(pady=4)

        ctk.CTkButton(
            sec, text="📂  Import CapFrameX file", font=_FX,
            fg_color="transparent", hover_color=_PANEL2,
            border_width=1, border_color=_BLUE,
            text_color=_BLUE, height=34, width=220,
            command=self._import_cfx).pack(side="left", padx=8)

        ctk.CTkButton(
            sec, text="CLEAR ALL", font=_FX,
            fg_color="transparent", hover_color=_PANEL2,
            border_width=1, border_color="gray30",
            text_color=_MUTED, height=34, width=100,
            command=self._clear_data).pack(side="left", padx=8)

        self._refresh_cards()

    def _refresh_src_badge(self):
        src = detect_source()
        colour = _SRC_COLOUR.get(src, _MUTED)
        label = _SRC_LABEL.get(src, src)
        self._src_badge.configure(
            text=f"Data source: {label}", text_color=colour)

        if src != "presentmon":
            self._pm_tip.configure(
                text="💡 For precise FPS: place PresentMon64.exe in the app folder. "
                     "Download: github.com/GameTechDev/PresentMon/releases")
        else:
            self._pm_tip.configure(text="")

    def _watch_for_game(self):
        if not self._live_running:
            return
        if is_valorant_running() and self._recording_mode is None:
            rec = load_benchmark()
            has_before = rec and rec.before
            has_opts = len(_get_recent_optimizations()) > 0

            if not has_before:
                self._bench_status.configure(
                    text="🎮 Valorant detected!  Press RECORD BEFORE to capture your baseline FPS.",
                    text_color=_GREEN)
            elif has_before and has_opts and (not rec or not rec.after):
                self._bench_status.configure(
                    text="✅ Optimizations applied!  Press RECORD AFTER to capture your new FPS.",
                    text_color=_ORANGE)

        self.after(3000, self._watch_for_game)

    def _start_recording(self, mode: str):
        if not is_valorant_running():
            self._show_game_prompt()
            return
        self._recording_mode = mode
        self._bench_status.configure(
            text=f"● Recording {mode.upper()} FPS — play normally, press STOP when done.",
            text_color=_RED)
        self._btn_before.configure(state="disabled")
        self._btn_after.configure(state="disabled")
        self._btn_stop.configure(state="normal")
        self._refresh_src_badge()
        start_capture()

    def _stop_recording(self):
        result = stop_capture()
        mode = self._recording_mode
        self._recording_mode = None
        self._btn_before.configure(state="normal")
        self._btn_after.configure(state="normal")
        self._btn_stop.configure(state="disabled")

        if result.samples == 0:
            self._bench_status.configure(
                text="⚠ No FPS data captured. Are you in an active match?",
                text_color=_RED)
            return

        self._save_result(mode, result)

    def _save_result(self, mode, result):
        if mode == "before":
            save_before(result)
            self._bench_status.configure(
                text=f"✔ BEFORE saved  —  avg {result.avg} fps  ({result.samples} frames)  |  "
                f"Now apply optimizations, then RECORD AFTER.",
                text_color=_GREEN)
        else:
            changes = _get_recent_optimizations()
            save_after(result, changes)
            self._bench_status.configure(
                text=f"✔ AFTER saved  —  avg {result.avg} fps  ({result.samples} frames)  |  "
                f"Check COMPARISON tab.",
                text_color=_GREEN)
        self._refresh_cards()

    def _clear_data(self):
        clear_benchmark()
        self._refresh_cards()
        self._bench_status.configure(
            text="Cleared. Record a fresh BEFORE benchmark.", text_color=_MUTED)

    def _show_game_prompt(self):
        popup = ctk.CTkToplevel(self)
        popup.title("VALOPT")
        popup.geometry("420x180")
        popup.configure(fg_color=_DARK)
        popup.resizable(False, False)
        popup.grab_set()
        ctk.CTkLabel(popup, text="⚠  VALORANT IS NOT RUNNING",
                     font=_FM, text_color=_RED).pack(pady=(28, 8))
        ctk.CTkLabel(popup,
                     text="Open Valorant and load into a match first.",
                     font=_FT, text_color=_WHITE).pack(pady=4)
        ctk.CTkButton(popup, text="OK", font=_FT,
                      fg_color=_RED, hover_color="#ff5f6b",
                      text_color=_WHITE, height=40, width=120,
                      command=popup.destroy).pack(pady=16)

    def _make_fps_card(self, parent, label, accent) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color=_PANEL,
                            corner_radius=10, width=270, height=240)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=label, font=_FM,
                     text_color=accent).pack(pady=(16, 6))
        for attr, title in (("avg", "AVG"), ("min", "MIN"), ("max", "MAX"), ("low1", "1% LOW")):
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=4)
            ctk.CTkLabel(row, text=f"{title}:", font=_FT,
                         text_color=_MUTED, width=80, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(row, text="--", font=_FT,
                               text_color=_WHITE, anchor="w")
            lbl.pack(side="left")
            setattr(card, f"_{attr}_lbl", lbl)
        card._src_lbl = ctk.CTkLabel(
            card, text="", font=_FX, text_color=_MUTED)
        card._src_lbl.pack(pady=(4, 10))
        return card

    def _fill_card(self, card, snap):
        if snap is None:
            for attr in ("avg", "min", "max", "low1"):
                getattr(card, f"_{attr}_lbl").configure(text="--")
            card._src_lbl.configure(text="")
            return
        card._avg_lbl.configure(text=f"{snap.avg:.1f} fps")
        card._min_lbl.configure(text=f"{snap.min:.1f} fps")
        card._max_lbl.configure(text=f"{snap.max:.1f} fps")
        card._low1_lbl.configure(text=f"{snap.low1:.1f} fps")
        card._src_lbl.configure(
            text=_SRC_LABEL.get(snap.source, snap.source),
            text_color=_SRC_COLOUR.get(snap.source, _MUTED))

    def _refresh_cards(self):
        rec = load_benchmark()
        if rec:
            self._fill_card(self._before_card, rec.before)
            self._fill_card(self._after_card,  rec.after)

    def _import_cfx(self):
        path = filedialog.askopenfilename(
            title="Select CapFrameX capture",
            filetypes=[("CapFrameX JSON", "*.json"), ("All files", "*.*")],
            initialdir=os.path.join(
                os.path.expanduser("~"), "Documents", "CapFrameX", "Captures"))
        if not path:
            return
        result = parse_capframex_file(path)
        if not result or result.samples == 0:
            self._bench_status.configure(
                text="⚠ Couldn't read FPS data from that file.", text_color=_RED)
            return
        self._show_cfx_dialog(result)

    def _show_cfx_dialog(self, result):
        popup = ctk.CTkToplevel(self)
        popup.title("Import CapFrameX")
        popup.geometry("420x220")
        popup.configure(fg_color=_DARK)
        popup.resizable(False, False)
        popup.grab_set()
        ctk.CTkLabel(popup, text="CAPFRAMEX DATA IMPORTED",
                     font=_FM, text_color=_BLUE).pack(pady=(20, 4))
        ctk.CTkLabel(popup,
                     text=f"avg {result.avg} fps  |  min {result.min}  |  "
                     f"max {result.max}  |  1%low {result.low1}\n({result.samples} frames)",
                     font=_FT, text_color=_WHITE, justify="center").pack(pady=4)
        ctk.CTkLabel(popup, text="Save as:", font=_FT,
                     text_color=_MUTED).pack(pady=(6, 4))
        row = ctk.CTkFrame(popup, fg_color="transparent")
        row.pack()
        for lbl, mode, fg, hov, tc in [
            ("BEFORE", "before", _RED,   "#ff5f6b", _WHITE),
            ("AFTER",  "after",  _GREEN, "#00ff88", _DARK),
        ]:
            ctk.CTkButton(row, text=lbl, font=_FT, fg_color=fg,
                          hover_color=hov, text_color=tc,
                          height=40, width=130,
                          command=lambda m=mode: [popup.destroy(),
                                                  self._save_result(m, result)]
                          ).pack(side="left", padx=8)

    def _build_comparison_tab(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        self._tab_frames["COMPARISON"] = f
        self._comp_frame = f

    def _refresh_comparison(self):
        for w in self._comp_frame.winfo_children():
            w.destroy()

        rec = load_benchmark()
        if not rec or not rec.before:
            ctk.CTkLabel(self._comp_frame,
                         text="No data yet.\nRecord BEFORE + AFTER in the FPS BENCHMARK tab.",
                         font=_FS, text_color=_MUTED, justify="center").pack(expand=True)
            return

        # chart
        cf = ctk.CTkFrame(self._comp_frame, fg_color=_PANEL, corner_radius=10)
        cf.pack(fill="x", pady=(8, 4))
        ctk.CTkLabel(cf, text="FPS COMPARISON", font=_FM,
                     text_color=_RED).pack(pady=(10, 2))
        canvas = ctk.CTkCanvas(
            cf, bg="#1a1a1a", highlightthickness=0, height=200)
        canvas.pack(fill="x", padx=16, pady=(0, 12))
        self.after(80, lambda: self._draw_chart(canvas, rec))

        # delta
        if rec.after:
            delta = rec.after.avg - rec.before.avg
            pct = (delta / rec.before.avg * 100) if rec.before.avg else 0
            arrow, col = ("▲", _GREEN) if delta >= 0 else ("▼", _RED)
            ctk.CTkLabel(self._comp_frame,
                         text=f"{arrow}  AVG FPS  {delta:+.1f}  ({pct:+.1f}%)",
                         font=_FM, text_color=col).pack(pady=6)

        # changes
        if rec.changes:
            ctk.CTkLabel(self._comp_frame, text="OPTIMIZATIONS APPLIED",
                         font=_FS, text_color=_GREEN).pack(pady=(4, 2))
            scroll = ctk.CTkScrollableFrame(
                self._comp_frame, fg_color=_PANEL, corner_radius=8, height=120)
            scroll.pack(fill="x", pady=(0, 6))
            for ch in rec.changes:
                row = ctk.CTkFrame(scroll, fg_color="transparent")
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(row, text="▸", font=_FX,
                             text_color=_GREEN, width=18).pack(side="left")
                ctk.CTkLabel(row, text=ch, font=_FX,
                             text_color=_WHITE, anchor="w").pack(side="left", padx=4)
        elif rec.after:
            ctk.CTkLabel(self._comp_frame,
                         text="(no optimization log found — run Recommended or Manual first)",
                         font=_FX, text_color=_MUTED).pack(pady=4)

    def _draw_chart(self, canvas, rec):
        canvas.update_idletasks()
        W = canvas.winfo_width() or 560
        H = canvas.winfo_height() or 200

        metrics = [("AVG", "avg"), ("MIN", "min"),
                   ("MAX", "max"), ("1%LOW", "low1")]
        pad_l, pad_r, pad_t, pad_b = 44, 16, 18, 36
        slot_w = (W - pad_l - pad_r) / len(metrics)
        bar_w = slot_w * 0.26

        all_vals = []
        for _, attr in metrics:
            all_vals.append(getattr(rec.before, attr, 0) or 0)
            if rec.after:
                all_vals.append(getattr(rec.after, attr, 0) or 0)
        max_val = max(all_vals) if all_vals else 1
        scale = (H - pad_t - pad_b) / max_val if max_val else 1

        for pct in (0.25, 0.5, 0.75, 1.0):
            y = H - pad_b - (max_val * pct * scale)
            canvas.create_line(pad_l, y, W - pad_r, y,
                               fill="#2a2a2a", dash=(4, 4))
            canvas.create_text(pad_l - 4, y, text=f"{int(max_val*pct)}",
                               fill=_MUTED, font=("Orbitron", 7), anchor="e")

        def bar(slot, which, value, colour):
            xc = pad_l + slot * slot_w + slot_w / 2
            offset = bar_w * 0.65 * (which - 0.5)
            x1, x2 = xc + offset - bar_w/2, xc + offset + bar_w/2
            y2, y1 = H - pad_b, max(H - pad_b - value * scale, pad_t)
            canvas.create_rectangle(x1, y1, x2, y2, fill=colour, outline="")
            canvas.create_text((x1+x2)/2, y1-5, text=f"{value:.0f}",
                               fill=colour, font=("Orbitron", 7))

        for i, (label, attr) in enumerate(metrics):
            bar(i, 0, getattr(rec.before, attr, 0) or 0, _RED)
            if rec.after:
                bar(i, 1, getattr(rec.after, attr, 0) or 0, _GREEN)
            xc = pad_l + i * slot_w + slot_w / 2
            canvas.create_text(xc, H - pad_b + 14, text=label,
                               fill=_WHITE, font=("Orbitron", 8, "bold"))

        for idx, (col, lbl) in enumerate(
                [(_RED, "BEFORE"), (_GREEN, "AFTER")] if rec.after
                else [(_RED, "BEFORE")]):
            y_off = 10 + idx * 16
            canvas.create_rectangle(W-110, y_off, W-98, y_off+10,
                                    fill=col, outline="")
            canvas.create_text(W-92, y_off+5, text=lbl,
                               fill=col, font=("Orbitron", 8), anchor="w")


def _get_recent_optimizations() -> list:
    try:
        import session_logger
        logs = session_logger.get_logs()
        keywords = ("Power Plan", "Extreme FPS", "RAM Clean", "Game DVR",
                    "Priority", "DNS", "Recommended", "Manual", "Applied",
                    "Windows", "NVIDIA", "Network", "Resolution", "Benchmark")
        result = []
        for entry in logs[-80:]:
            if any(k in entry for k in keywords):
                # Strip "[HH:MM:SS] " prefix and " -> SUCCESS" suffix
                clean = entry.split("] ", 1)[-1]
                clean = clean.replace(
                    " -> SUCCESS", "").replace(" -> FAILED", " ⚠").strip()
                if clean and clean not in result:
                    result.append(clean)
        return result[-20:]
    except Exception:
        return []
