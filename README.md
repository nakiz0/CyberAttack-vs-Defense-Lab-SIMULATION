# Cyber Attack vs Defense Lab
## Educational Cybersecurity Simulation Tool

> ⚠️ **SAFE SIMULATION ONLY** — No real network activity, no real hacking, no real brute force.
> Everything is 100% in-memory simulation for educational purposes.

---

## Project Structure

```
cyber_lab/
├── main.py       — GUI application (Tkinter, dark theme)
├── logic.py      — Attack & defense simulation engine + command parser
├── system.py     — Virtual OS: filesystem, password, port definitions
└── README.md     — This file
```

---

## Requirements

- Python 3.8+
- Tkinter (bundled with most Python installs)

No third-party packages required.

---

## How to Run

```bash
cd cyber_lab
python main.py
```

---

## Quick Start Guide

### As Defender (right panel):
1. Set a custom password (e.g. `mysecurepass`) and click **SET**
2. Enable **Firewall**, **IDS**, and **Honeypot** checkboxes
3. Add/remove files from the virtual filesystem

### As Attacker (left panel):
1. Click **HOST SCAN** → **PORT SCAN** to recon the target
2. Edit the wordlist field, then click **BRUTE FORCE**
3. Or click **EXPLOIT** to try a generic exploit
4. If access is granted, use the file buttons or terminal commands

### Terminal (bottom):
Type commands and press Enter or click **▶ RUN**

```
scan              # Host discovery
ports             # Port scan
brute admin 1234  # Brute force with custom wordlist
exploit           # Generic exploit
ls                # List files (requires access)
cat secrets.txt   # Read file (requires access)
setpass mypass    # Change system password
firewall on       # Enable firewall
ids on            # Enable IDS
honeypot on       # Enable honeypot
status            # Show system status
reset             # Reset to defaults
help              # Full command reference
```

Terminal supports **command history** with ↑ / ↓ arrow keys.

---

## Keyboard Shortcuts

| Shortcut | Action         |
|----------|----------------|
| Ctrl+L   | Clear console  |
| Ctrl+R   | Reset session  |
| ↑ / ↓    | Command history|

---

## Defense Logic

| Defenses Active | Exploit Outcome              |
|-----------------|------------------------------|
| None            | Always succeeds              |
| 1–2 enabled     | ~38% bypass chance           |
| All 3 enabled   | Always blocked               |

Brute force is blocked immediately when **both** Firewall AND IDS are active.

---

## Build Standalone Executable (PyInstaller)

### Install PyInstaller:
```bash
pip install pyinstaller
```

### Build:
```bash
cd cyber_lab
pyinstaller --onefile --windowed --name "CyberLab" main.py
```

### Options explained:
- `--onefile`   — Pack everything into a single .exe / binary
- `--windowed`  — No terminal window on Windows/macOS
- `--name`      — Output executable name

The final binary will be in `dist/CyberLab` (or `dist/CyberLab.exe` on Windows).

### Windows icon (optional):
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name "CyberLab" main.py
```

---

## Architecture Notes

- **system.py** — Pure data layer. `VirtualSystem` class holds all mutable state.
  No network code anywhere in this file.
- **logic.py** — Business logic layer. `AttackEngine` produces `(success, lines, delay)`
  tuples. `CommandParser` maps terminal input to engine calls or defender mutations.
- **main.py** — Presentation layer. All simulation runs in background threads
  (`threading.Thread`) so the GUI never freezes. Thread results are posted back
  to the main thread via `tk.after()`.

---

## Educational Notes

This tool simulates real attack/defense concepts:
- **Host discovery** → Nmap -sn style ping sweep
- **Port scanning** → TCP SYN stealth scan
- **Brute force** → Dictionary credential attack
- **Exploit** → Remote code execution via unpatched CVE
- **Firewall** → Packet filtering / connection reset
- **IDS** → Signature-based intrusion detection
- **Honeypot** → Deceptive system to fingerprint attackers

All simulated. Safe for classroom and self-study use.
