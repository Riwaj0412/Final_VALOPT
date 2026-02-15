import subprocess
import winsound


def set_max_power():
    try:
        # Standard GUID for 'High Performance'
        guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

        # creationflags=0x08000000 prevents the CMD window from flashing
        subprocess.run(
            f"powercfg /setactive {guid}",
            shell=True,
            check=True,
            creationflags=0x08000000
        )

        # --- SOUND ARMED: Heavy Tech Thud ---
        # Frequency: 400Hz, Duration: 150ms
        winsound.Beep(400, 150)

        return True
    except Exception as e:
        print(f"Power Plan Error: {e}")
        # --- ERROR SOUND: Low Jarring Tone ---
        winsound.Beep(200, 400)
        return False
