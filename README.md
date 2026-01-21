# DeskPilot

DeskPilot is a Windows-only, local-first PySide6 desktop automation command center. It focuses on practical daily workflows: launching app/URL profiles, rendering templates into clipboard text, and lightweight browser workflows.

## Non-goals
- Not a full RPA platform/recorder
- No cloud sync or accounts by default
- No AI features unless explicitly opt-in and isolated

## Setup
- Python 3.10+ recommended
- Create a virtual environment and install dependencies (Windows, copy/paste):
  ```
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  pip install pyinstaller
  ```

## Run
- From the repo root (auto-builds `dist/DeskPilot.exe` each run):
  ```
  python -m deskpilot.main
  ```
- Skip the auto build step:
  ```
  python -m deskpilot.main --no-build-exe
  ```
- Build only (no app UI):
  ```
  python -m deskpilot.main --build-exe
  ```
- Exit the virtual environment when you're done:
  ```
  deactivate
  ```

## Config & extensibility (power-user friendly)
On first run, DeskPilot creates a `config/` folder (portable mode) or `%USERPROFILE%\.deskpilot\config\` with example files:
- `actions.yaml`: data-driven actions (what to do)
- `templates.yaml`: Jinja templates + field definitions (auto-form capable)
- `profiles.yaml`: launcher targets for Work/Study/etc.

You can create your own actions by editing YAML—no Python required for common workflows like launch profiles, render templates, copy to clipboard, and wait steps.

## Roadmap (draft)
See the draft product roadmap for planned UX, automation, editor, and performance improvements:
`docs/roadmap.md`.

## Sharing (later concept)
Action packs will be importable/exportable as a simple `.zip` containing `actions.yaml`, `templates.yaml`, `profiles.yaml` and assets.
