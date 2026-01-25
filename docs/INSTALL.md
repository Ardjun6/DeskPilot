# 📦 Installation Guide

This guide will walk you through installing DeskPilot on your Windows machine.

---

## 📋 Requirements

- **Operating System**: Windows 10 or Windows 11
- **Python**: 3.10 or higher
- **Disk Space**: ~100 MB

---

## 🚀 Installation Methods

### Method 1: Quick Install (Recommended)

1. **Download** the latest release from GitHub or extract the zip file

2. **Open PowerShell** in the DeskPilot folder:
   - Right-click in the folder → "Open in Terminal"
   - Or press `Shift + Right-click` → "Open PowerShell window here"

3. **Create a virtual environment**:
   ```powershell
   python -m venv .venv
   ```

4. **Activate the virtual environment**:
   ```powershell
   .venv\Scripts\activate
   ```

5. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

6. **Run DeskPilot**:
   ```powershell
   python -m deskpilot.main
   ```

---

### Method 2: Using pip (Coming Soon)

```bash
pip install deskpilot
deskpilot
```

---

## 📦 Dependencies

DeskPilot uses the following Python packages:

| Package | Version | Purpose |
|---------|---------|---------|
| PySide6 | 6.6.1 | Qt UI framework |
| pyautogui | 0.9.54 | Mouse/keyboard automation |
| pynput | 1.7.6 | Input recording |
| keyboard | 0.13.5 | Global hotkeys |
| pyperclip | 1.8.2 | Clipboard access |
| Jinja2 | 3.1.4 | Template engine |
| PyYAML | 6.0.2 | YAML configuration |
| pydantic | 2.6.1 | Data validation |

All dependencies are listed in `requirements.txt` and will be installed automatically.

---

## 🔧 Post-Installation Setup

### 1. First Run

On first run, DeskPilot will create a config folder at:
```
%USERPROFILE%\.deskpilot\
```

This folder contains:
- `actions.json` - Your custom actions
- `launchers.json` - Launcher configurations
- `templates.json` - Text templates
- `settings.json` - App preferences

### 2. System Tray

DeskPilot runs in the system tray by default. Look for the icon near your clock.

### 3. Hotkeys

Default hotkeys (customizable):
- `Ctrl+K` - Command palette
- `Ctrl+Shift+Q` - Quick actions widget
- `Ctrl+Shift+V` - Clipboard history

---

## 🏃 Running DeskPilot

### Standard Run
```powershell
python -m deskpilot.main
```

### Run Without Splash Screen
```powershell
python -m deskpilot.main --no-splash
```

### Run With Specific Theme
```powershell
python -m deskpilot.main --theme productivity
```

Available themes: `productivity`, `calm`, `contrast`, `playful`, `glass`

---

## 🔨 Building an Executable (Optional)

To create a standalone `.exe` file:

1. **Install PyInstaller**:
   ```powershell
   pip install pyinstaller
   ```

2. **Build**:
   ```powershell
   python -m deskpilot.main --build-exe
   ```

3. **Find the executable** in the `dist/` folder

---

## ❌ Uninstallation

1. Delete the DeskPilot folder
2. Delete the config folder:
   ```powershell
   Remove-Item -Recurse ~\.deskpilot
   ```
3. (If installed via pip): `pip uninstall deskpilot`

---

## 🐛 Troubleshooting Installation

### "Python is not recognized"
- Install Python from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

### "pip is not recognized"
```powershell
python -m ensurepip --upgrade
```

### PySide6 installation fails
```powershell
pip install --upgrade pip
pip install PySide6
```

### Permission errors
Run PowerShell as Administrator

### "Module not found" errors
Make sure you activated the virtual environment:
```powershell
.venv\Scripts\activate
```

---

## 📞 Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Open an issue on GitHub
- Check existing issues for solutions

---

[← Back to README](../README.md)
