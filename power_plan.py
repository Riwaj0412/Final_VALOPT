import subprocess
import session_logger


def set_max_power():
    """Activates High Performance mode and logs the event."""
    try:
        # High Performance GUID
        guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

        # Run the command silently
        subprocess.run(
            f"powercfg /setactive {guid}",
            shell=True,
            check=True,
            creationflags=0x08000000
        )

        # --- CRITICAL: Log the success ---
        session_logger.add_log("Power Plan: High Performance Activated")
        return True

    except Exception as e:
        # --- CRITICAL: Log the failure ---
        session_logger.add_log(f"Power Plan Error: {str(e)}", "FAILED")
        return False
