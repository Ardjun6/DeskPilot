# ✨ Features

Detailed documentation of all DeskPilot features.

---

## ⚡ Actions System

### What are Actions?
Actions are automated tasks that can be triggered manually, via hotkey, or from the system tray. Each action consists of one or more steps that execute in sequence.

### Step Types

#### 🖥️ Open Application
Launches an application from its file path.

```json
{
  "type": "open_app",
  "params": {
    "path": "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
  }
}
```

#### 🌐 Open URL
Opens a URL in the default browser.

```json
{
  "type": "open_url",
  "params": {
    "url": "https://github.com"
  }
}
```

#### ⏱️ Delay
Waits for a specified number of seconds.

```json
{
  "type": "delay",
  "params": {
    "seconds": 2.5
  }
}
```

#### 🖱️ Click
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

#### ⌨️ Type Text
Types text at the current cursor position.

```json
{
  "type": "type_text",
  "params": {
    "text": "Hello, World!"
  }
}
```

#### 🔤 Hotkey
Presses a keyboard shortcut.

```json
{
  "type": "hotkey",
  "params": {
    "keys": ["ctrl", "shift", "n"]
  }
}
```

#### 📋 Paste
Pastes the current clipboard content.

```json
{
  "type": "paste",
  "params": {}
}
```

---

## 🔧 Visual Workflow Builder

### Overview
The Workflow Builder provides a drag-and-drop interface for creating actions without writing JSON.

### Creating a Workflow

1. **Add Steps**: Drag step types from the palette to the canvas
2. **Configure**: Click ✏️ on any step to edit its parameters
3. **Reorder**: Use ↑↓ buttons to change step order
4. **Delete**: Click 🗑️ to remove unwanted steps
5. **Save**: Enter a name and click "Save Action"

### Step Palette
The left panel shows all available step types:
- 🖥️ Open Application
- 🌐 Open URL
- ⏱️ Wait/Delay
- 🖱️ Mouse Click
- ⌨️ Type Text
- 🔤 Press Hotkey
- 📋 Paste Clipboard

---

## 🎬 Action Recorder

### Overview
Record your mouse and keyboard to automatically create actions.

### Recording Options

| Option | Description |
|--------|-------------|
| Record mouse clicks | Captures click positions |
| Record keyboard | Captures key presses |
| Countdown | Delay before recording starts |

### Recorded Actions

The recorder captures:
- **Mouse clicks**: Position and button (left/right)
- **Key presses**: Individual keys
- **Hotkeys**: Key combinations (Ctrl+C, etc.)
- **Delays**: Time between actions (>0.5s)

### Tips for Recording

1. **Use countdown** to switch windows before recording
2. **Move slowly** - quick movements may be missed
3. **Review steps** before saving
4. **Delete mistakes** using the delete button
5. **Test thoroughly** before relying on the action

---

## 📋 Clipboard Manager

### Features

| Feature | Description |
|---------|-------------|
| Auto-tracking | Monitors clipboard automatically |
| History | Stores up to 50 entries |
| Search | Find past clips by content |
| Pin | Keep important items permanently |
| Quick paste | One-click to paste any entry |

### Keyboard Shortcut
`Ctrl+Shift+V` - Open clipboard popup anywhere

### Data Storage
Clipboard history is stored in memory and cleared when the app closes. Pinned items persist across sessions.

---

## 🖱️ Mouse Jiggler

### Movement Patterns

| Pattern | Movement | Visibility |
|---------|----------|------------|
| Subtle (1px) | 1 pixel right, then back | Barely visible |
| Circle | Tiny circular motion | Slightly visible |
| Random | Random 3px movements | Visible |
| Square | Small square pattern | Visible |
| Invisible | No movement (API call) | Invisible |

### Caffeine Mode ☕
Prevents sleep without any visible mouse movement. Uses system API calls to keep the PC awake.

### Schedule 📅
Automatically start and stop jiggling based on:
- **Start time**: When to begin (e.g., 9:00 AM)
- **End time**: When to stop (e.g., 5:00 PM)
- **Days**: Which days of the week

### Statistics 📊
Tracks:
- Total sessions
- Total jiggles
- Total uptime (hours/minutes)

---

## 📝 Text Templates

### Overview
Store and quickly insert frequently used text snippets.

### Jinja2 Support
Templates support Jinja2 syntax for dynamic content:

```jinja2
Dear {{ recipient }},

Thank you for your inquiry about {{ product }}.

{% if discount %}
Special offer: {{ discount }}% off!
{% endif %}

Best regards,
{{ sender }}
```

### Variables
When using a template with variables, DeskPilot prompts for values.

---

## 🎨 Themes

### Available Themes

| Theme | Style |
|-------|-------|
| Productivity | Clean, professional blue |
| Calm | Soft, relaxing green |
| Contrast | High contrast dark |
| Playful | Vibrant purple/pink |
| Glass | Modern dark with transparency |

### Changing Themes
1. Use the Theme dropdown in the toolbar
2. Or go to Settings tab
3. Changes apply immediately

---

## 📌 Quick Actions Widget

### Features
- **Always on top**: Stays visible over other windows
- **Draggable**: Move anywhere on screen
- **Compact**: Shows only action buttons
- **Pin toggle**: Enable/disable always-on-top

### Opening the Widget
- Press `Ctrl+Shift+Q`
- Click 📌 in the toolbar
- Right-click tray → Quick Actions Widget

### Displayed Actions
Shows your favorite actions, or all actions if none are favorited.

---

## 🔔 System Tray Integration

### Tray Icon
DeskPilot adds an icon to your system tray (notification area).

### Tray Menu
Right-click the tray icon for:
- **Show DeskPilot**: Open main window
- **Quick Actions**: Submenu of your actions
- **Start/Stop Jiggle**: Toggle jiggler
- **Clipboard History**: Open clipboard popup
- **Quick Actions Widget**: Show floating widget
- **Settings**: Open settings tab
- **Quit**: Exit completely

### Minimize to Tray
Closing the main window minimizes to tray instead of quitting. Use Quit from tray menu to exit completely.

### Notifications
DeskPilot shows notifications for:
- Minimized to tray confirmation
- Action completion (optional)

---

## ⌨️ Global Hotkeys

### Default Hotkeys

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Command palette |
| `Ctrl+Shift+Q` | Quick widget |
| `Ctrl+Shift+V` | Clipboard |

### Custom Hotkeys
Assign hotkeys to actions in:
- Action right-click menu → Set Hotkey
- Workflow Builder → Hotkey field
- Edit JSON tab

### Hotkey Format
- `Ctrl+A`
- `Ctrl+Shift+A`
- `Alt+F4`
- `Ctrl+Alt+Delete` (not recommended)

---

## 🔍 Command Palette

### Overview
Quick access to all actions without using the mouse.

### Opening
Press `Ctrl+K` or click "⌘ Commands" button

### Usage
1. Open command palette
2. Type to search actions
3. Use ↑↓ to navigate
4. Press Enter to run
5. Press Esc to close

### Recent Actions
Recently used actions appear at the top with ⏱ icon.

---

[← Back to README](../README.md)
