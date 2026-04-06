import subprocess
import time
import os
from pynput import keyboard

# Setup storage folder
save_path = os.path.expanduser("~/hacking_case/screenshots")
os.makedirs(save_path, exist_ok=True)

print(f"--- Forensic Camera Active ---")
print(f"Saving to: {save_path}")
print("Press 'Enter' in any window to snap a screenshot. Press 'ESC' to stop.")

def on_press(key):
    try:
        if key == keyboard.Key.enter:
            # Short delay to let the terminal render your output
            time.sleep(0.3) 
            filename = f"evidence_{int(time.time())}.png"
            full_path = os.path.join(save_path, filename)
            
            # Using the native GNOME tool which works on modern Kali
            subprocess.run(["gnome-screenshot", "-f", full_path])
            print(f"[+] Captured: {filename}")
            
    except Exception as e:
        print(f"Error: {e}")

    if key == keyboard.Key.esc:
        print("Stopping camera...")
        return False

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
