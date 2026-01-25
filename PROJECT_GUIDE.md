# 🗺️ DeskPilot Project Guide

## Where to Find Everything

This guide explains where each part of the code lives and what it does.

---

## 📁 Folder Structure

```
DeskPilot-main/
│
├── deskpilot/                    # Main source code
│   │
│   ├── main.py                   # 🚀 APP ENTRY POINT - Start here!
│   ├── app.py                    # Creates main window and connects everything
│   │
│   ├── ui/                       # 🎨 USER INTERFACE
│   │   ├── theme_manager.py      # ⭐ COLORS & STYLING - Edit themes here!
│   │   ├── main_window.py        # Main application window
│   │   ├── sidebar.py            # Navigation sidebar
│   │   ├── splash_screen.py      # Startup animation
│   │   ├── system_tray.py        # System tray icon/menu
│   │   ├── command_palette.py    # Ctrl+K command search
│   │   │
│   │   ├── views/                # 📑 MAIN TABS/PAGES
│   │   │   ├── action_view.py    # Actions tab
│   │   │   ├── template_view.py  # Templates tab
│   │   │   ├── workflow_builder_view.py  # Workflow builder tab
│   │   │   ├── recorder_view.py  # Action recorder tab
│   │   │   ├── jiggle_view.py    # Mouse jiggler tab
│   │   │   ├── settings_view.py  # Settings tab
│   │   │   └── launcher_editor_view.py  # JSON editor tab
│   │   │
│   │   └── widgets/              # 🧩 REUSABLE COMPONENTS
│   │       ├── quick_actions_widget.py   # Floating quick actions
│   │       ├── clipboard_manager.py      # Clipboard history
│   │       ├── coordinate_picker.py      # Mouse position picker
│   │       ├── app_picker.py             # Application selector
│   │       ├── action_list.py            # Action cards list
│   │       └── ...
│   │
│   ├── actions/                  # ⚡ AUTOMATION ENGINE
│   │   ├── engine.py             # Runs actions
│   │   ├── steps.py              # ⭐ ALL STEP TYPES - Add new steps here!
│   │   └── ...
│   │
│   ├── config/                   # 💾 CONFIGURATION
│   │   ├── config_manager.py     # Loads/saves settings
│   │   └── models.py             # Data structures
│   │
│   ├── utils/                    # 🔧 UTILITIES
│   │   ├── hotkeys.py            # Global hotkey handling
│   │   ├── clipboard.py          # Clipboard operations
│   │   └── ...
│   │
│   └── assets/                   # 📦 ASSETS
│       └── styles/
│           └── dark.qss          # CSS-like stylesheet (optional)
│
├── docs/                         # 📖 Documentation
└── requirements.txt              # Python dependencies
```

---

## 🎨 HOW TO CHANGE STYLING

### Option 1: Edit Theme Colors (Recommended)

**File:** `deskpilot/ui/theme_manager.py`

Look for the `THEMES` dictionary (around line 80). Each theme has a `colors` dictionary:

```python
"glass": Theme(
    name="Modern Glass",
    is_dark=True,
    colors={
        "bg": "#0f1419",          # Main background
        "surface": "#1a212b",      # Card backgrounds
        "accent": "#3b9eff",       # Buttons, highlights
        "text": "#e6edf5",         # Main text
        # ... more colors
    },
)
```

**To change a color:**
1. Find the color you want to change
2. Replace the hex code (e.g., `#3b9eff` → `#ff0000`)
3. Save and restart the app

### Option 2: Edit Widget Styles

**File:** `deskpilot/ui/theme_manager.py`

Look for the `_build_stylesheet` method (around line 350). This contains CSS-like styling:

```python
QPushButton {
    background-color: {c['surface']};
    border-radius: {r}px;
    padding: 8px 16px;
}
```

### Option 3: Create Your Own Theme

1. Copy an existing theme in `THEMES` dictionary
2. Give it a new name (e.g., `"my_theme"`)
3. Change the colors
4. Run with: `python -m deskpilot.main --theme my_theme`

---

## 🔧 HOW TO ADD NEW FEATURES

### Add a New Step Type (Workflow Action)

**File:** `deskpilot/actions/steps.py`

1. Create a new class:
```python
class MyNewStep(Step):
    type = "my_step"
    
    def __init__(self, my_param: str) -> None:
        self.my_param = my_param
    
    def preview(self, ctx: StepContext) -> str:
        return f"Do something with {self.my_param}"
    
    def run(self, ctx: StepContext, result: RunResult) -> None:
        # Your code here
        result.add_log("INFO", "Did something!")
```

2. Register it in `step_from_def` function:
```python
if step_type == "my_step":
    return MyNewStep(my_param=str(params.get("my_param", "")))
```

3. Add to workflow builder in `deskpilot/ui/views/workflow_builder_view.py`:
```python
STEP_TYPES = {
    # ... existing steps
    "my_step": {
        "name": "My New Step",
        "icon": "✨",
        "color": "#ff0000",
        "desc": "Does something cool",
    },
}
```

### Add a New Tab/View

1. Create file in `deskpilot/ui/views/my_view.py`
2. Add to sidebar in `deskpilot/ui/sidebar.py` (NAV_ITEMS list)
3. Add to main_window in `deskpilot/ui/main_window.py` (stack widget)

---

## 🎯 QUICK REFERENCE

| What You Want | Where To Go |
|---------------|-------------|
| Change colors | `ui/theme_manager.py` → THEMES dictionary |
| Change button styles | `ui/theme_manager.py` → _build_stylesheet() |
| Add workflow step | `actions/steps.py` + `ui/views/workflow_builder_view.py` |
| Change sidebar items | `ui/sidebar.py` → NAV_ITEMS |
| Edit main layout | `ui/main_window.py` |
| Change action cards | `ui/widgets/action_list.py` |
| Edit quick actions | `ui/widgets/quick_actions_widget.py` |
| Change hotkey behavior | `utils/hotkeys.py` |

---

## 🏃 Running the App

```bash
# Normal start
python -m deskpilot.main

# With specific theme
python -m deskpilot.main --theme glass

# Skip splash screen
python -m deskpilot.main --no-splash
```

---

## 📝 Notes

- All styling uses **Qt StyleSheets** (similar to CSS)
- Colors are defined as **hex codes** (e.g., `#3b9eff`)
- The app auto-reloads themes when you change them in Settings
- User data is stored in `~/.deskpilot/` on Windows

