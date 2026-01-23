testing:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
python -m deskpilot.main
python -m deskpilot.main --no-build-exe
```

Quick start developers:
quick start:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
python -m deskpilot.main
python -m deskpilot.main --build-exe
.\dist\DeskPilot.exe
```

explaining the application
DeskPilot is a Windows-only, local-first desktop automation command center built with PySide6. It helps you run saved actions, launch app/URL profiles, render templates into clipboard-ready text, and execute lightweight macros with in-app logs.
