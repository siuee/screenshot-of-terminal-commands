📸 TermSnap
A lightweight Python tool that runs any terminal command and saves its output as a styled PNG screenshot — perfect for reports, documentation, and CTF writeups.

✨ Features

Runs any shell command and captures its full output
Saves output as a clean, dark-themed terminal PNG
Timestamped filenames — no overwrites
Falls back to a styled HTML file if Pillow isn't installed
Zero config — works out of the box on Kali Linux

🚀 Usage
bashpython3 termsnap.py "<command>"
Examples
bashpython3 termsnap.py "nmap -sV 192.168.1.1"
python3 termsnap.py whoami
python3 termsnap.py "ls -la /etc"
python3 termsnap.py netstat -tulnp
For commands that need root:
bashsudo python3 termsnap.py "nmap -sS 192.168.1.0/24"

📁 Output
Each run generates a PNG file in the current directory:
termsnap_nmap_20250406_143022.png
