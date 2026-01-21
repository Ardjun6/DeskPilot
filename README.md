# DeskPilot

DeskPilot is a Windows-only, local-first PySide6 desktop automation command center. It focuses on practical daily workflows: launching app/URL profiles, rendering templates into clipboard text, and lightweight browser workflows.

## Non-goals
- Not a full RPA platform/recorder
- No cloud sync or accounts by default
- No AI features unless explicitly opt-in and isolated

## Setup
- Python 3.10+ recommended
- These steps are written for Windows. Use the copy/paste blocks below.
- If you are new to Python: a **virtual environment** is a safe folder for app dependencies.

### Option A: Quick start (developers)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
python -m deskpilot.main
```

### Option B: Step-by-step (first-time users)
1. **Open Command Prompt** in the project folder.
2. **Create a virtual environment** (one-time):
   ```
   python -m venv .venv
   ```
3. **Activate it** (you should see `(.venv)` in your prompt):
   ```
   .venv\Scripts\activate
   ```
4. **Install the app dependencies**:
   ```
   pip install -r requirements.txt
   ```
5. **Install the builder** (needed for the `.exe`):
   ```
   pip install pyinstaller
   ```
6. **Run DeskPilot**:
   ```
   python -m deskpilot.main
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

## Build (Windows .exe)
- Install PyInstaller: `pip install pyinstaller`
- Build an executable: `python -m deskpilot.main --build-exe`
- The output is written to `dist/DeskPilot.exe`

## Config & extensibility (power-user friendly)
On first run, DeskPilot creates a `config/` folder (portable mode) or `%USERPROFILE%\.deskpilot\config\` with example files:
- `actions.json`: data-driven actions (what to do)
- `templates.json`: Jinja templates + field definitions (auto-form capable)
- `profiles.json`: launcher targets for Work/Study/etc.

You can create your own actions by editing JSON—no Python required for common workflows like launch profiles, render templates, copy to clipboard, and wait steps.

## Roadmap (draft)
See the draft product roadmap for planned UX, automation, editor, and performance improvements:
`docs/roadmap.md`.

## Sharing (later concept)
Action packs will be importable/exportable as a simple `.zip` containing `actions.json`, `templates.json`, `profiles.json` and assets.
