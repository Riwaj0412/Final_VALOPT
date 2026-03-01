import time
import subprocess

# Global list to hold session logs
session_history = []


def add_log(action, status="SUCCESS"):
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {action} -> {status}"
    session_history.append(entry)


def get_logs():
    return session_history


def restore_defaults():
    try:
        # Standard Windows Balanced Power GUID
        balanced_guid = "381b4222-f694-41f0-9685-ff5bb260df2e"
        subprocess.run(
            f"powercfg /setactive {balanced_guid}", shell=True, creationflags=0x08000000)

        add_log("RESTORE: Settings reverted to Windows Defaults", "COMPLETED")
        return True
    except Exception as e:
        add_log(f"RESTORE FAILED: {str(e)}", "ERROR")
        return False
