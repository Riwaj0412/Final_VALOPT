import customtkinter as ctk
import styles
import threading
import time
import socket
import platform


class NetworkMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")
        self.back_command = back_command
        self.stop_thread = False

        # EXPANDED REGIONS: Added LATAM, Brazil, Korea, and Middle East
        self.regions = {
            "ASIA-PACIFIC": {
                "Mumbai": ("13.126.0.1", 80),
                "Singapore": ("18.136.0.1", 443),
                "Sydney": ("13.236.193.132", 80),
                "Tokyo": ("52.192.0.1", 443),
                "Hong Kong": ("18.162.0.1", 80)
            },
            "NORTH AMERICA": {
                "US West": ("13.52.4.1", 80),
                "US East": ("18.204.0.1", 80),
                "US Central": ("18.191.0.1", 80)
            },
            "EUROPE": {
                "Frankfurt": ("35.156.0.1", 443),
                "London": ("3.8.0.1", 80),
                "Paris": ("15.188.0.1", 80),
                "Warsaw": ("52.28.0.1", 80)
            },
            "LATAM / BRAZIL": {
                "Sao Paulo": ("15.228.0.1", 443),
                "Santiago": ("18.231.0.1", 80),
                "Mexico City": ("18.204.0.1", 80)
            },
            "KOREA": {
                "Seoul": ("15.164.0.1", 443)
            },
            "MIDDLE EAST": {
                "Bahrain": ("15.185.0.1", 80),
                "UAE": ("15.184.0.1", 80)
            }
        }

        self.setup_ui()
        self.show_main_options()

    def setup_ui(self):
        self.title_label = ctk.CTkLabel(
            self, text="NETWORK OPTIMIZATION", font=styles.FONT_ORBITRON_MD, text_color="#ff4655")
        self.title_label.pack(pady=(20, 20))

        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True, padx=40)

        self.back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", hover_color="#ff5f6b", text_color="white",
            height=60, width=300, corner_radius=4, command=self.handle_back
        )
        self.back_btn.pack(side="bottom", pady=30)

    def show_region_selection(self):
        self.clear_view()
        self.current_state = "REGIONS"

        # Using a scrollable frame for region selection to handle many regions
        scroll_region = ctk.CTkScrollableFrame(
            self.view_container, fg_color="transparent", height=400)
        scroll_region.pack(fill="both", expand=True)

        for r in self.regions.keys():
            b = ctk.CTkButton(scroll_region, text=f"[ {r} ]", font=styles.FONT_ORBITRON_SM,
                              fg_color="transparent", border_width=1, border_color="#ff4655",
                              height=60, width=320,
                              command=lambda name=r: self.show_server_pings(name))
            styles.apply_tactical_style(b)
            b.pack(pady=10, anchor="center")

    def show_server_pings(self, region_name):
        self.clear_view()
        self.current_state = "SERVERS"
        self.stop_thread = False

        ctk.CTkLabel(self.view_container, text=f"REGION: {region_name}",
                     font=styles.FONT_ORBITRON_SM, text_color="white").pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(
            self.view_container, fg_color="#1a252e", height=350)
        scroll_frame.pack(fill="both", expand=True)

        self.server_labels = {}
        for server, data in self.regions[region_name].items():
            row = ctk.CTkFrame(
                scroll_frame, fg_color="transparent", width=400, height=40)
            row.pack(pady=5, anchor="center")
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=server, font=styles.FONT_ORBITRON_SM,
                         text_color="white").pack(side="left", padx=10)

            p_lbl = ctk.CTkLabel(
                row, text="---", font=styles.FONT_ORBITRON_SM, text_color="#ff4655")
            p_lbl.pack(side="right", padx=10)

            self.server_labels[data] = p_lbl

        threading.Thread(target=self.pro_ping_loop, daemon=True).start()

    def pro_ping_loop(self):
        while not self.stop_thread:
            for (ip, port), label in self.server_labels.items():
                if self.stop_thread:
                    break

                latency = self.get_tcp_latency(ip, port)

                if label.winfo_exists():
                    display = f"{latency}ms" if latency else "BUSY"
                    label.configure(text=display)
                else:
                    return
            time.sleep(1.5)

    def get_tcp_latency(self, ip, port):
        try:
            start = time.perf_counter()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((ip, port))
            s.close()
            return int((time.perf_counter() - start) * 1000)
        except:
            return None

    def clear_view(self):
        self.stop_thread = True
        for child in self.view_container.winfo_children():
            child.destroy()

    def show_main_options(self):
        self.clear_view()
        self.current_state = "MAIN"
        f = ctk.CTkFrame(self.view_container, fg_color="transparent")
        f.pack(expand=True)
        for t, c in [("[ CHECK PING ]", self.show_region_selection), ("[ FLUSH DNS ]", self.run_flush_dns)]:
            b = ctk.CTkButton(f, text=t, font=styles.FONT_ORBITRON_SM, fg_color="transparent",
                              border_width=2, border_color="#ff4655", height=100, width=300, command=c)
            styles.apply_tactical_style(b)
            b.pack(pady=10)

    def run_flush_dns(self):
        import subprocess
        subprocess.run("ipconfig /flushdns", shell=True,
                       creationflags=0x08000000)
        self.title_label.configure(text="DNS PURGED", text_color="white")
        self.after(2000, lambda: self.title_label.configure(
            text="NETWORK OPTIMIZATION", text_color="#ff4655"))

    def handle_back(self):
        if self.current_state == "MAIN":
            self.back_command()
        elif self.current_state == "REGIONS":
            self.show_main_options()
        elif self.current_state == "SERVERS":
            self.show_region_selection()
