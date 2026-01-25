from __future__ import annotations

import json
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QScrollArea,
)

from ...config.config_manager import ConfigManager
from ..theme_manager import ThemeManager
from ..widgets.grid_layout import GridCanvas


# Complete JSON example with all launcher step types
LAUNCHER_JSON_EXAMPLE = '''{
  "config_version": 1,
  "launchers": [
    {
      "id": "work_morning",
      "name": "Morning Work Setup",
      "description": "Opens all work apps and websites for the day",
      "hotkey": "Ctrl+Shift+W",
      "enabled": true,
      "schedule_time": null,
      "schedule_delay": null,
      "steps": [
        {
          "type": "open_app",
          "params": {
            "path": "C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe"
          }
        },
        {
          "type": "delay",
          "params": {
            "seconds": 2
          }
        },
        {
          "type": "open_url",
          "params": {
            "url": "https://mail.google.com"
          }
        },
        {
          "type": "open_url",
          "params": {
            "url": "https://calendar.google.com"
          }
        },
        {
          "type": "open_app",
          "params": {
            "path": "C:\\\\Program Files\\\\Slack\\\\Slack.exe"
          }
        }
      ]
    },
    {
      "id": "study_session",
      "name": "Study Session",
      "description": "Opens study resources with a 5-minute delay",
      "hotkey": null,
      "enabled": true,
      "schedule_time": null,
      "schedule_delay": 300,
      "steps": [
        {
          "type": "open_url",
          "params": {
            "url": "https://www.khanacademy.org"
          }
        },
        {
          "type": "open_url",
          "params": {
            "url": "https://www.notion.so"
          }
        }
      ]
    },
    {
      "id": "auto_click_example",
      "name": "Auto Click Example",
      "description": "Demonstrates click automation (use with caution)",
      "hotkey": null,
      "enabled": false,
      "schedule_time": "09:00",
      "schedule_delay": null,
      "steps": [
        {
          "type": "open_app",
          "params": {
            "path": "notepad.exe"
          }
        },
        {
          "type": "delay",
          "params": {
            "seconds": 1
          }
        },
        {
          "type": "click",
          "params": {
            "x": 500,
            "y": 300
          }
        },
        {
          "type": "type_text",
          "params": {
            "text": "Hello from DeskPilot!"
          }
        }
      ]
    }
  ]
}'''


STEP_REFERENCE = """
## Launcher Step Types Reference

### open_app
Opens an application by file path.
```json
{
  "type": "open_app",
  "params": {
    "path": "C:\\\\Program Files\\\\App\\\\app.exe"
  }
}
```

### open_url  
Opens a URL in the default browser.
```json
{
  "type": "open_url",
  "params": {
    "url": "https://example.com"
  }
}
```

### delay
Waits for a specified number of seconds.
```json
{
  "type": "delay",
  "params": {
    "seconds": 5
  }
}
```

### click
Clicks at specific screen coordinates.
```json
{
  "type": "click",
  "params": {
    "x": 500,
    "y": 300
  }
}
```

### type_text
Types text at the current cursor position.
```json
{
  "type": "type_text",
  "params": {
    "text": "Hello World"
  }
}
```

### paste
Pastes clipboard content.
```json
{
  "type": "paste",
  "params": {}
}
```

### hotkey
Presses a keyboard shortcut.
```json
{
  "type": "hotkey",
  "params": {
    "keys": ["ctrl", "c"]
  }
}
```

## Launcher Properties

| Property | Type | Description |
|----------|------|-------------|
| id | string | Unique identifier |
| name | string | Display name |
| description | string | What it does |
| hotkey | string/null | Global hotkey (e.g., "Ctrl+Shift+L") |
| enabled | bool | Active or Inactive |
| schedule_time | string/null | Run at specific time (HH:MM) |
| schedule_delay | int/null | Delay in seconds before running |
| steps | array | List of step objects |
"""


class LauncherEditorView(QWidget):
    """JSON editor for creating and editing launchers with comprehensive documentation."""

    def __init__(
        self,
        config_manager: ConfigManager,
        theme_manager: ThemeManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self._build_ui()
        self._connect_signals()
        self._load_current()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("🚀 Launcher JSON Editor")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()
        
        self.load_example_btn = QPushButton("Load Example")
        self.validate_btn = QPushButton("Validate JSON")
        self.save_btn = QPushButton("Save")
        self.save_btn.setProperty("primary", True)
        
        header.addWidget(self.load_example_btn)
        header.addWidget(self.validate_btn)
        header.addWidget(self.save_btn)
        layout.addLayout(header)

        # Splitter for editor and reference
        splitter = QSplitter(Qt.Horizontal)

        # Left: JSON Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        editor_label = QLabel("launchers.json")
        editor_label.setObjectName("ActionDesc")
        editor_layout.addWidget(editor_label)
        
        self.json_editor = QPlainTextEdit()
        self.json_editor.setObjectName("JsonEditor")
        self.json_editor.setPlaceholderText("Paste or write your launcher JSON here...")
        self.json_editor.setStyleSheet("""
            QPlainTextEdit {
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
            }
        """)
        editor_layout.addWidget(self.json_editor)
        
        splitter.addWidget(editor_widget)

        # Right: Reference documentation
        ref_widget = QWidget()
        ref_layout = QVBoxLayout(ref_widget)
        ref_layout.setContentsMargins(0, 0, 0, 0)
        
        ref_label = QLabel("Step Reference")
        ref_label.setObjectName("ActionDesc")
        ref_layout.addWidget(ref_label)
        
        self.reference_text = QPlainTextEdit()
        self.reference_text.setReadOnly(True)
        self.reference_text.setPlainText(STEP_REFERENCE)
        self.reference_text.setStyleSheet("""
            QPlainTextEdit {
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
            }
        """)
        ref_layout.addWidget(self.reference_text)
        
        splitter.addWidget(ref_widget)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter, 1)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("ActionDesc")
        layout.addWidget(self.status_label)

    def _connect_signals(self) -> None:
        self.load_example_btn.clicked.connect(self._load_example)
        self.validate_btn.clicked.connect(self._validate_json)
        self.save_btn.clicked.connect(self._save_json)

    def _load_current(self) -> None:
        """Load current launchers.json if it exists."""
        path = self.config_manager.config_dir / "launchers.json"
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                # Pretty print it
                data = json.loads(content)
                self.json_editor.setPlainText(json.dumps(data, indent=2))
                self.status_label.setText(f"Loaded: {path}")
            except Exception as e:
                self.status_label.setText(f"Error loading file: {e}")
        else:
            self.status_label.setText("No launchers.json found - use 'Load Example' to start")

    def _load_example(self) -> None:
        """Load the example JSON into the editor."""
        self.json_editor.setPlainText(LAUNCHER_JSON_EXAMPLE)
        self.status_label.setText("Loaded example - modify and save to create your launchers")

    def _validate_json(self) -> None:
        """Validate the JSON in the editor."""
        text = self.json_editor.toPlainText()
        if not text.strip():
            self.status_label.setText("⚠ Editor is empty")
            return
        
        try:
            data = json.loads(text)
            
            # Validate structure
            if "launchers" not in data:
                self.status_label.setText("⚠ Missing 'launchers' array")
                return
            
            if not isinstance(data["launchers"], list):
                self.status_label.setText("⚠ 'launchers' must be an array")
                return
            
            # Validate each launcher
            for i, launcher in enumerate(data["launchers"]):
                if "id" not in launcher:
                    self.status_label.setText(f"⚠ Launcher {i+1} missing 'id'")
                    return
                if "name" not in launcher:
                    self.status_label.setText(f"⚠ Launcher {i+1} missing 'name'")
                    return
                if "steps" not in launcher:
                    self.status_label.setText(f"⚠ Launcher {i+1} missing 'steps'")
                    return
            
            count = len(data["launchers"])
            active = sum(1 for l in data["launchers"] if l.get("enabled", True))
            self.status_label.setText(f"✓ Valid JSON - {count} launchers ({active} active, {count - active} inactive)")
            
        except json.JSONDecodeError as e:
            self.status_label.setText(f"✗ Invalid JSON: {e}")

    def _save_json(self) -> None:
        """Save the JSON to launchers.json."""
        text = self.json_editor.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Error", "Editor is empty")
            return
        
        try:
            data = json.loads(text)
            
            # Ensure config_version
            if "config_version" not in data:
                data["config_version"] = 1
            
            path = self.config_manager.config_dir / "launchers.json"
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            
            count = len(data.get("launchers", []))
            self.status_label.setText(f"✓ Saved {count} launchers to {path.name}")
            
            # Refresh main window hotkeys
            main = self.window()
            if hasattr(main, "refresh_hotkeys"):
                main.refresh_hotkeys()
            
            # Refresh action view to show new launchers
            if hasattr(main, "action_view"):
                main.action_view.refresh()
            
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save: {e}")

    def filter_items(self, text: str) -> None:
        """Search within the JSON editor."""
        # Could implement find functionality here
        pass
