# Seriphai's Terminal Livesplit

A terminal-based “LiveSplit”-style race timer built in Python.

Designed for keyboard or controller input with persistent bindings and a clean terminal UI.

---

## Features

- Terminal UI entry screen:
  - Start Race
  - Bind Keys (rebind anytime)
  - Quit
- Persistent key/controller bindings
- Bind each action to **keyboard OR controller**
  - LAP (Start / Split)
  - STOP (End race)
  - RESET (Clear laps + return to waiting)
- Anti-“stuck controller button” protection during binding
- Post-race prompt:
  - Save results to `.txt`
  - Leave without saving
- Modular code structure:
  - `terminal_livesplit.py` (entrypoint)
  - `binding.py` (binding logic + config)
  - `race.py` (in-race timing UI)
  - `fileExport.py` (export helpers)

---

## Requirements

- Python 3.10+
- `pygame`
- A terminal that supports `curses`

---

## 🚨 Windows Important Note

This application uses **curses**, which is built into Python on Linux/macOS.

**Native Windows Python does NOT include curses by default.**

You have three options:

### ✅ Recommended: Use WSL (Windows Subsystem for Linux)
Install WSL and run the Linux version of this app inside Ubuntu (or similar).
This provides full curses compatibility and is the smoothest experience.

### ⚠️ Native Windows Python
The included Windows installer will create a virtual environment and install dependencies,
but the curses UI may fail unless you use a Python distribution that provides curses support.

### 🔮 Future Improvement
If needed, the UI layer could be swapped to something cross-platform like:
- `textual`
- `urwid`
- or a lightweight GUI wrapper

For now: **WSL is strongly recommended on Windows.**

---

## Quick Start

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python terminal_livesplit.py
