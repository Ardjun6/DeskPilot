# DeskPilot

DeskPilot is a PySide6 desktop automation command center for Windows. It provides configurable templates, launch profiles, macros, and flows, and is designed so users can add their own actions and content via configuration files or new subclasses.

## Setup
- Python 3.10+ recommended.
- Create a virtual environment and install dependencies:  
  `python -m venv .venv`  
  `.venv\Scripts\activate`  
  `pip install -r requirements.txt`

## Run
- From the repo root: `python -m deskpilot.main`

## Extend
- Add or edit user data in the config files created by `ConfigManager` (profiles, templates, macros, flows, hotkeys).
- Implement new actions by subclassing `Action` in `deskpilot/actions/base.py` and registering them.
- Add new views under `deskpilot/ui/views/` and wire them into the sidebar and stacked widget.

## Packaging (later)
- PyInstaller example (to refine after implementation):  
  `pyinstaller --onefile --windowed --name DeskPilot --icon=resources/icon.ico --add-data "resources;resources" --hidden-import PySide6.QtWidgets --hidden-import PySide6.QtGui --hidden-import PySide6.QtCore --hidden-import jinja2 --hidden-import keyboard --hidden-import pyautogui deskpilot/main.py`
# DeskPilot

**Your personal digital command center for Windows**  
Automate repetitive tasks with ease: write professional emails, run keyboard/mouse macros, open research tabs in one click, launch app/URL profiles, and more — all from a sleek PySide6 desktop app.

Packaged as a single standalone `.exe` — no installation hassle.

![DeskPilot Screenshot](path/to/screenshot.png)  <!-- Add a nice GIF or screenshot later -->

## Features (MVP)
- **Templates** — Generate emails/job applications with Jinja2 + simple forms → clipboard or draft
- **Macros & Hotkeys** — Record/play sequences, global shortcuts for signatures, folder creation, desktop cleanup
- **Browser Workflows** — "Research mode": multi-tab Google + custom sites, paste outlines
- **App Launcher Profiles** — Work/Study setups: open apps, URLs, timers
- **Configurable & Extensible** — JSON/YAML storage, modular Action system

Built with: Python • PySide6 • Jinja2 • pyautogui/keyboard • pyperclip • PyInstaller

[Quick Start](#installation) | [Screenshots](#screenshots) | [Contributing](#contributing) | [Roadmap](#roadmap)
