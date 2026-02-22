import customtkinter as ctk
import psutil
import GPUtil
import styles


class BenchmarkMenu(ctk.CTkFrame):
    def __init__(self, master, back_cmd):
        super().__init__(master, fg_color="transparent")

        self.label = ctk.CTkLabel(self, text="LIVE SYSTEM MONITOR", font=(
            "Orbitron", 40, "bold"), text_color="#ff4655")
        self.label.pack(pady=(40, 20))

        self.stats_area = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_area.pack(pady=20, expand=True)

        self.cpu_label = ctk.CTkLabel(self.stats_area, text="CPU USAGE: 0.0%", font=(
            "Orbitron", 24, "bold"), text_color="white")
        self.cpu_label.pack(pady=15)

        self.gpu_label = ctk.CTkLabel(self.stats_area, text="GPU USAGE: 0.0%", font=(
            "Orbitron", 24, "bold"), text_color="white")
        self.gpu_label.pack(pady=15)

        self.ram_label = ctk.CTkLabel(self.stats_area, text="RAM USAGE: 0.0%", font=(
            "Orbitron", 24, "bold"), text_color="white")
        self.ram_label.pack(pady=15)

        self.back_btn = ctk.CTkButton(self, text="[ BACK ]", font=styles.FONT_ORBITRON_SM,
                                      fg_color="#ff4655", height=60, width=320, command=back_cmd)
        self.back_btn.pack(side="bottom", pady=40)

        self.update_metrics()

    def update_metrics(self):
        cpu_use = psutil.cpu_percent()
        ram_use = psutil.virtual_memory().percent

        gpu_text = "GPU: N/A"
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_text = f"GPU: {gpus[0].load*100:.1f}% | TEMP: {gpus[0].temperature}°C"
        except:
            pass

        self.cpu_label.configure(text=f"CPU USAGE: {cpu_use:.1f}%")
        self.ram_label.configure(text=f"RAM USAGE: {ram_use:.1f}%")
        self.gpu_label.configure(text=gpu_text)

        self.after(1000, self.update_metrics)
