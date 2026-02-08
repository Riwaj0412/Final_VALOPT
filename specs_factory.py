import customtkinter as ctk
import psutil
import wmi
import os
from PIL import Image

def get_real_specs():
    """Directly queries the motherboard for your exact Acer Nitro specs."""
    specs = {"cpu": "Detecting...", "gpu": "Detecting...", "ram": "16 GB", "os": "Windows 11"}
    
    try:
        c = wmi.WMI()
        
        # 1. Get EXACT CPU Name
        for cpu in c.Win32_Processor():
            specs["cpu"] = cpu.Name.replace("(TM)", "").replace("(R)", "").strip()

        # 2. Get EXACT GPU Name
        gpus = []
        for gpu in c.Win32_VideoController():
            gpus.append(gpu.Name)
        
        # Filter for the powerful RTX card, not the integrated Intel one
        dedicated = [g for g in gpus if "NVIDIA" in g or "RTX" in g]
        specs["gpu"] = dedicated[0] if dedicated else gpus[0]
        
        # 3. RAM calculation
        specs["ram"] = f"{round(psutil.virtual_memory().total / (1024**3))} GB"

    except Exception as e:
        specs["cpu"] = "ACCESS DENIED"
        specs["gpu"] = "ACCESS DENIED"
        print(f"System Error: {e}")
        
    return specs

def build_specs_grid(parent, node_widgets):
    """Rebuilds the grid with your real hardware names and icons."""
    specs = get_real_specs()
    
    spec_data = [
        ("CORE PROCESSOR", specs["cpu"], "cpu_icon.png"),
        ("SYSTEM MEMORY", specs["ram"], "ram_icon.png"),
        ("GRAPHICS CARD", specs["gpu"], "gpu_icon.png"),
        ("OS KERNEL", "Windows 11", "os_icon.png")
    ]

    for i, (title, value, icon_name) in enumerate(spec_data):
        card = ctk.CTkFrame(parent, fg_color="#0f1923", border_color="#ff4655", border_width=1, corner_radius=10)
        card.grid(row=i//2, column=i%2, padx=15, pady=15, sticky="nsew")
        
        # Load your icons from the assets folder
        try:
            img_path = os.path.join(os.path.dirname(__file__), "assets", icon_name)
            img = ctk.CTkImage(light_image=Image.open(img_path), size=(35, 35))
            ctk.CTkLabel(card, image=img, text="").pack(pady=(15, 0))
        except:
            pass

        ctk.CTkLabel(card, text=title, font=("Impact", 16), text_color="#ff4655").pack(pady=(5, 2))
        # 'wraplength' ensures the long i7 and RTX names fit in the boxes
        ctk.CTkLabel(card, text=value, font=("Arial", 11, "bold"), 
                     text_color="white", wraplength=230).pack(pady=(0, 20))
        
        node_widgets[f"card_{i}"] = card
        card.grid_remove() 

    parent.columnconfigure((0, 1), weight=1)