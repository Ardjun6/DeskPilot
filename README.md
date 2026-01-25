# ✈️ DeskPilot

**Desktop Automation Made Easy**

DeskPilot is a powerful desktop automation tool for Windows that helps you automate repetitive tasks, manage your clipboard, keep your PC awake, and boost your productivity.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Features

### ⚡ Actions & Automation
- Create custom automation workflows
- Chain multiple steps together (open apps, click, type, hotkeys)
- Trigger actions with global hotkeys
- Run actions from system tray

### 🔧 Visual Workflow Builder
- Drag-and-drop interface - no coding required
- Build complex automations visually
- Edit step parameters with simple forms
- Save and reuse workflows

### 🎬 Action Recorder
- Record your mouse clicks and keyboard presses
- Automatically captures delays between actions
- Edit recorded steps before saving
- Perfect for creating automations quickly

### 📋 Clipboard Manager
- Automatic clipboard history tracking
- Search through past clips
- Pin important items
- Quick paste with Ctrl+Shift+V

### 🖱️ Mouse Jiggler
- Keep your PC awake without touching it
- Multiple movement patterns (subtle, circle, random, invisible)
- ☕ Caffeine Mode - prevent sleep without visible movement
- 📅 Schedule - auto start/stop based on time
- 📊 Statistics tracking

### 📝 Text Templates
- Store frequently used text snippets
- Variables support with Jinja2
- Quick insertion with hotkeys

### 🎨 Beautiful UI
- 5 polished themes (Productivity, Calm, Contrast, Playful, Glass)
- Animated splash screen
- System tray integration
- Floating quick actions widget

---

## 🚀 Quick Start

```bash
# Clone or download
git clone https://github.com/ardjun6/DeskPilot.git
cd DeskPilot

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run
python -m deskpilot.main
```

See [docs/INSTALL.md](docs/INSTALL.md) for detailed installation instructions.

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [INSTALL.md](docs/INSTALL.md) | Installation guide |
| [USAGE.md](docs/USAGE.md) | How to use DeskPilot |
| [FEATURES.md](docs/FEATURES.md) | Detailed feature documentation |
| [CONFIGURATION.md](docs/CONFIGURATION.md) | Configuration options |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history |

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open command palette |
| `Ctrl+Shift+Q` | Show quick actions widget |
| `Ctrl+Shift+V` | Open clipboard history |

---

## 🛠️ Built With

- **[PySide6](https://doc.qt.io/qtforpython/)** - Qt for Python (UI framework)
- **[PyAutoGUI](https://pyautogui.readthedocs.io/)** - Mouse and keyboard automation
- **[pynput](https://pynput.readthedocs.io/)** - Input monitoring for recorder
- **[Jinja2](https://jinja.palletsprojects.com/)** - Template engine

---

## 📁 Project Structure

```
DeskPilot/
├── deskpilot/
│   ├── actions/          # Action execution engine
│   ├── config/           # Configuration management
│   ├── ui/
│   │   ├── views/        # Main UI views
│   │   ├── widgets/      # Reusable widgets
│   │   └── ...
│   ├── utils/            # Utilities
│   └── main.py           # Entry point
├── docs/                 # Documentation
├── requirements.txt
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for productivity enthusiasts**
