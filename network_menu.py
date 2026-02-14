import customtkinter as ctk
import styles
import windows_button
import threading


class NetworkMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        super().__init__(master, fg_color="transparent")
        self.back_command = back_command

        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True)

        self.global_back_btn = ctk.CTkButton(
            self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
            fg_color="#ff4655", height=60, width=300, command=self.handle_global_back
        )
        self.global_back_btn.pack(side="bottom", pady=40)

        self.show_main_network_options()

    def clear_view(self):
        for child in self.view_container.winfo_children():
            child.destroy()

    def show_main_network_options(self):
        self.clear_view()
        self.global_back_btn.pack(
            side="bottom", pady=40)

        ctk.CTkLabel(self.view_container, text="NETWORK UTILS",
                     font=styles.FONT_ORBITRON_MD, text_color="#ff4655").pack(pady=40)

        btn_flush = ctk.CTkButton(self.view_container, text="FLUSH DNS", font=styles.FONT_ORBITRON_SM,
                                  width=500, height=80, fg_color="transparent", border_width=2,
                                  border_color="#3d799d", command=windows_button.flush_dns)
        styles.apply_tactical_style(btn_flush)
        btn_flush.pack(pady=10)

        btn_ping = ctk.CTkButton(self.view_container, text="CHECK PING", font=styles.FONT_ORBITRON_SM,
                                 width=500, height=80, fg_color="transparent", border_width=2,
                                 border_color="#808080", command=self.show_region_selection)
        styles.apply_tactical_style(btn_ping)
        btn_ping.pack(pady=10)

    def show_region_selection(self):
        self.clear_view()
        self.global_back_btn.pack(side="bottom", pady=40)

        ctk.CTkLabel(self.view_container, text="SELECT REGION",
                     font=styles.FONT_ORBITRON_MD, text_color="#ff4655").pack(pady=30)

        regions = {
            "ASIA-PACIFIC": ["Mumbai", "Singapore", "Sydney", "Hong Kong", "Tokyo"],
            "EUROPE": ["London", "Frankfurt", "Paris", "Madrid", "Istanbul"],
            "NORTH AMERICA": ["N. Virginia", "Texas", "California"],
            "LATAM / BRAZIL": ["Sao Paulo", "Santiago", "Mexico City"],
            "KOREA": ["Seoul"]
        }

        for region_name, cities in regions.items():
            btn = ctk.CTkButton(self.view_container, text=region_name, font=styles.FONT_ORBITRON_SM,
                                width=500, height=60, fg_color="transparent", border_width=2,
                                border_color="#3d799d",
                                command=lambda r=region_name, c=cities: self.show_latency_details(r, c))
            styles.apply_tactical_style(btn)
            btn.pack(pady=8)

    def show_latency_details(self, region, cities):
        self.clear_view()
        self.global_back_btn.pack_forget()

        LatencyDetailView(self.view_container, region, cities,
                          self.show_region_selection).pack(fill="both", expand=True)

    def handle_global_back(self):
        try:
            current_title = self.view_container.winfo_children()[
                0].cget("text")
            if current_title == "SELECT REGION":
                self.show_main_network_options()
            else:
                self.back_command()
        except:
            self.back_command()


class LatencyDetailView(ctk.CTkFrame):
    def __init__(self, master, region_name, cities, back_to_regions):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(self, text=f"{region_name} LATENCY",
                     font=styles.FONT_ORBITRON_MD, text_color="#ff4655").pack(pady=40)

        self.results_frame = ctk.CTkFrame(
            self, fg_color="#1a1a1a", border_width=1, border_color="#333333")
        self.results_frame.pack(pady=20, padx=50, fill="x")

        self.city_labels = {}
        for city in cities:
            lbl = ctk.CTkLabel(self.results_frame, text=f"{city.upper()}: Pinging...",
                               font=styles.FONT_ORBITRON_SM, text_color="gray")
            lbl.pack(pady=10)
            self.city_labels[city] = lbl

        threading.Thread(target=self.run_pings, args=(
            cities,), daemon=True).start()

        ctk.CTkButton(self, text="[ BACK TO REGIONS ]", font=styles.FONT_ORBITRON_SM,
                      fg_color="#ff4655", height=50, width=250, command=back_to_regions).pack(side="bottom", pady=40)

    def run_pings(self, cities):
        for city in cities:
            ms = windows_button.get_latency(city)
            color = "#00ff7f" if "ms" in ms else "#ff4655"
            self.city_labels[city].configure(
                text=f"{city.upper()}: {ms}", text_color=color)
