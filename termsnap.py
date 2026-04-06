#!/usr/bin/env python3
"""
termsnap.py - Run a command and save its output as a terminal screenshot PNG
Usage:
    python3 termsnap.py <command>
    python3 termsnap.py "nmap -sV 192.168.1.1"
    python3 termsnap.py ls -la
"""

import subprocess
import sys
import os
import shutil
from datetime import datetime

# ── Optional: pillow for PNG rendering ────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# ── Config ────────────────────────────────────────────────────────────────────
FONT_SIZE     = 14
PADDING       = 20          # px around text
LINE_SPACING  = 4           # extra px between lines
TAB_WIDTH     = 4           # spaces per tab
MAX_COLS      = 200         # wrap lines longer than this
BG_COLOR      = (18, 18, 18)        # terminal background
FG_COLOR      = (204, 204, 204)     # default text colour
TITLE_BG      = (40, 40, 40)        # title bar background
TITLE_FG      = (200, 200, 200)
BTN_RED       = (255, 96, 96)
BTN_YLW       = (255, 200, 60)
BTN_GRN       = (50, 200, 80)
TITLE_HEIGHT  = 32          # px for the top title bar

# Fonts to try (first found wins)
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
    "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf",
]


def find_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_line(line, max_cols):
    """Hard-wrap a single line at max_cols characters."""
    line = line.replace("\t", " " * TAB_WIDTH)
    if len(line) <= max_cols:
        return [line]
    chunks = []
    while len(line) > max_cols:
        chunks.append(line[:max_cols])
        line = "    " + line[max_cols:]   # indent continuation
    chunks.append(line)
    return chunks


def render_png(command_str, output_text, out_path):
    """Render output_text as a terminal-style PNG and save to out_path."""
    font = find_font(FONT_SIZE)

    # Build list of display lines
    raw_lines = output_text.splitlines()
    display_lines = []
    for rl in raw_lines:
        display_lines.extend(wrap_line(rl, MAX_COLS))

    # Measure character cell size using a dummy draw
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), "W", font=font)
    char_w = bbox[2] - bbox[0]
    char_h = bbox[3] - bbox[1] + LINE_SPACING

    # Canvas dimensions
    max_line_len = max((len(l) for l in display_lines), default=40)
    canvas_w = max(600, max_line_len * char_w + PADDING * 2)
    canvas_h = TITLE_HEIGHT + len(display_lines) * char_h + PADDING * 2

    img = Image.new("RGB", (canvas_w, canvas_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # ── Title bar ────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, canvas_w, TITLE_HEIGHT], fill=TITLE_BG)
    # Traffic-light buttons
    for i, color in enumerate([BTN_RED, BTN_YLW, BTN_GRN]):
        cx = 14 + i * 22
        cy = TITLE_HEIGHT // 2
        draw.ellipse([cx-6, cy-6, cx+6, cy+6], fill=color)
    # Title text
    title = f"  {command_str}"
    draw.text((canvas_w // 2 - len(title) * char_w // 2, 7),
              title, font=font, fill=TITLE_FG)

    # ── Terminal text ─────────────────────────────────────────────────────────
    y = TITLE_HEIGHT + PADDING
    for line in display_lines:
        draw.text((PADDING, y), line, font=font, fill=FG_COLOR)
        y += char_h

    img.save(out_path, "PNG")
    print(f"[✓] Screenshot saved → {out_path}")


def render_fallback_html(command_str, output_text, out_path):
    """
    Fallback when Pillow isn't available: save a self-contained HTML file
    that looks like a terminal.  You can open it in a browser and print/
    screenshot it from there.
    """
    escaped = (output_text
               .replace("&", "&amp;")
               .replace("<", "&lt;")
               .replace(">", "&gt;"))
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{command_str}</title>
<style>
  body {{ margin: 0; background: #121212; }}
  .titlebar {{
    background: #282828;
    height: 32px;
    display: flex;
    align-items: center;
    padding: 0 14px;
    gap: 10px;
    font-family: monospace;
    font-size: 13px;
    color: #c8c8c8;
  }}
  .btn {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
  .red {{ background: #ff6060; }}
  .ylw {{ background: #ffc83c; }}
  .grn {{ background: #32c850; }}
  .title-text {{ margin-left: auto; margin-right: auto; }}
  pre {{
    margin: 0;
    padding: 20px;
    background: #121212;
    color: #cccccc;
    font-family: 'DejaVu Sans Mono', 'Liberation Mono', monospace;
    font-size: 14px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
  }}
</style>
</head>
<body>
  <div class="titlebar">
    <span class="btn red"></span>
    <span class="btn ylw"></span>
    <span class="btn grn"></span>
    <span class="title-text">{command_str}</span>
  </div>
  <pre>{escaped}</pre>
</body>
</html>"""
    with open(out_path, "w") as f:
        f.write(html)
    print(f"[✓] HTML terminal saved → {out_path}")
    print("    Open in a browser, then use browser screenshot or Ctrl+P → Save as PDF.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 termsnap.py <command> [args...]")
        print("       python3 termsnap.py \"nmap -sV 192.168.1.1\"")
        sys.exit(1)

    # Build command string
    if len(sys.argv) == 2:
        # Single quoted argument like "nmap -sV host"
        cmd_str  = sys.argv[1]
        cmd_list = sys.argv[1:]   # let shell parse it
        use_shell = True
    else:
        cmd_list = sys.argv[1:]
        cmd_str  = " ".join(cmd_list)
        use_shell = False

    # ── Run the command ───────────────────────────────────────────────────────
    print(f"[*] Running: {cmd_str}")
    try:
        result = subprocess.run(
            cmd_list if not use_shell else cmd_str,
            shell=use_shell,
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = result.stdout
        if result.stderr:
            output += result.stderr
    except FileNotFoundError:
        print(f"[!] Command not found: {cmd_list[0]}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("[!] Command timed out after 300 seconds.")
        sys.exit(1)

    if not output.strip():
        output = "(no output)"

    # Print output to terminal as well
    print(output)

    # ── Generate filename ─────────────────────────────────────────────────────
    ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_cmd    = cmd_str.split()[0].replace("/", "_").replace(".", "_")
    base_name   = f"termsnap_{safe_cmd}_{ts}"

    # ── Save screenshot ───────────────────────────────────────────────────────
    if HAS_PILLOW:
        out_path = f"{base_name}.png"
        render_png(cmd_str, output, out_path)
    else:
        out_path = f"{base_name}.html"
        print("[!] Pillow not found – generating HTML fallback.")
        print("    Install Pillow for real PNG output:  sudo apt update && sudo apt install -y python3-pil")
        render_fallback_html(cmd_str, output, out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
