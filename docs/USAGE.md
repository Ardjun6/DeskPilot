# 📘 Usage Guide

Learn how to use DeskPilot to automate your daily tasks.

---

## 🎯 Getting Started

When you first launch DeskPilot, you'll see:
- **Sidebar** on the left with 8 tabs
- **Main content area** in the center
- **Log panel** at the bottom
- **System tray icon** near your clock

---

## 📑 Tabs Overview

### 1. ⚡ Actions
The main hub for running automations.

**Features:**
- View all your actions
- Filter by favorites
- Sort by name
- Run actions with one click
- Preview action steps
- Right-click for more options

**How to run an action:**
1. Click the `▶ Run` button on any action card
2. Or use the assigned hotkey
3. Or right-click the system tray → Quick Actions

---

### 2. 📝 Templates
Store and use text snippets.

**Features:**
- Create text templates with variables
- Copy to clipboard instantly
- Use Jinja2 syntax for dynamic content

**Example template:**
```
Hello {{ name }},

Thank you for your message regarding {{ topic }}.

Best regards,
{{ signature }}
```

---

### 3. 🔧 Workflow Builder
Create automations visually without coding.

**How to create a workflow:**
1. Drag step types from the left panel
2. Drop them onto the canvas
3. Click ✏️ to edit step parameters
4. Use ↑↓ to reorder steps
5. Enter a name and click "Save Action"

**Available step types:**
| Step | Description |
|------|-------------|
| 🖥️ Open Application | Launch any program |
| 🌐 Open URL | Open a website |
| ⏱️ Wait/Delay | Pause for X seconds |
| 🖱️ Mouse Click | Click at coordinates |
| ⌨️ Type Text | Type text at cursor |
| 🔤 Press Hotkey | Press key combinations |
| 📋 Paste Clipboard | Paste current clipboard |

---

### 4. 🎬 Recorder
Record your actions to create automations.

**How to record:**
1. Choose what to record (mouse, keyboard, or both)
2. Set countdown time (to switch windows)
3. Click "Start Recording"
4. Perform your actions
5. Click "Stop Recording" or press the stop button
6. Review and edit recorded steps
7. Save as a new action

**Tips:**
- Delays are automatically captured
- Delete unwanted steps before saving
- Test your recording before relying on it

---

### 5. 📋 Clipboard
Access your clipboard history.

**Features:**
- Automatic tracking of copied text
- Search through history
- Pin important items
- Quick paste

**Shortcuts:**
- `Ctrl+Shift+V` - Open clipboard popup anywhere

---

### 6. 🖱️ Jiggle
Keep your PC awake.

**Patterns:**
| Pattern | Description |
|---------|-------------|
| Subtle (1px) | Barely noticeable movement |
| Circle | Tiny circular motion |
| Random | Random small movements |
| Square | Small square pattern |
| Invisible | No visible movement (system call) |

**Features:**
- ☕ **Caffeine Mode** - Prevent sleep without moving mouse
- 📅 **Schedule** - Auto start/stop at specific times
- 📊 **Statistics** - Track sessions and uptime

**Schedule example:**
- Start: 9:00 AM
- End: 5:00 PM
- Days: Mon, Tue, Wed, Thu, Fri

---

### 7. 🚀 Edit JSON
Advanced launcher configuration.

**For power users** who want to edit action JSON directly.

**Example launcher JSON:**
```json
{
  "config_version": 1,
  "launchers": [
    {
      "id": "morning_routine",
      "name": "Morning Setup",
      "description": "Opens work apps",
      "hotkey": "Ctrl+Shift+M",
      "enabled": true,
      "steps": [
        {"type": "open_app", "params": {"path": "C:\\...\\outlook.exe"}},
        {"type": "delay", "params": {"seconds": 2}},
        {"type": "open_url", "params": {"url": "https://mail.google.com"}}
      ]
    }
  ]
}
```

---

### 8. ⚙️ Settings
Configure DeskPilot preferences.

**Options:**
- Theme selection
- Navigation position
- Startup behavior
- Hotkey configuration

---

## 🎹 Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open command palette |
| `Ctrl+Shift+Q` | Quick actions widget |
| `Ctrl+Shift+V` | Clipboard history |
| Custom | Your action hotkeys |

---

## 📌 Quick Actions Widget

A floating mini-panel for fast access to actions.

**To open:**
- Press `Ctrl+Shift+Q`
- Or click 📌 in the toolbar
- Or right-click tray → Quick Actions Widget

**Features:**
- Always on top (toggleable)
- Draggable anywhere
- Shows favorite actions
- One-click execution

---

## 🔔 System Tray

DeskPilot lives in your system tray.

**Tray menu options:**
- Show DeskPilot
- Quick Actions (submenu)
- Start/Stop Jiggle
- Clipboard History
- Quick Actions Widget
- Settings
- Quit

**Behaviors:**
- Closing the window minimizes to tray
- Double-click tray icon to show window
- Right-click for menu

---

## 💡 Tips & Tricks

### Create a morning routine
1. Go to Workflow Builder
2. Add: Open Outlook → Delay 2s → Open Browser → Open Gmail
3. Assign hotkey `Ctrl+Shift+M`
4. Run every morning!

### Quick text expansion
1. Create a template with your email signature
2. Assign a hotkey
3. Press hotkey anywhere to paste

### Stay online during meetings
1. Go to Jiggle tab
2. Set pattern to "Invisible"
3. Enable Caffeine Mode
4. Click Start

### Record complex tasks
1. Go to Recorder
2. Set 5 second countdown
3. Start recording
4. Perform the task slowly
5. Save and assign hotkey

---

## ❓ FAQ

**Q: Can I run DeskPilot at startup?**
A: Coming soon! For now, create a shortcut in your Startup folder.

**Q: Are my actions synced across devices?**
A: Not currently. Actions are stored locally in `~/.deskpilot/`

**Q: Can I share actions with others?**
A: Yes! Export the JSON from Edit JSON tab and share the file.

---

[← Back to README](../README.md)
