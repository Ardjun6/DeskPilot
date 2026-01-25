# ⚙️ Configuration Guide

DeskPilot stores configuration files in your user directory.

---

## 📁 Configuration Location

```
%USERPROFILE%\.deskpilot\
├── actions.json      # Your custom actions
├── launchers.json    # Launcher configurations
├── templates.json    # Text templates
└── settings.json     # App preferences
```

On Windows, this is typically:
```
C:\Users\YourName\.deskpilot\
```

---

## 📄 Configuration Files

### actions.json

Stores all your custom actions.

```json
{
  "config_version": 1,
  "actions": [
    {
      "id": "unique_id",
      "name": "Action Name",
      "description": "What this action does",
      "hotkey": "Ctrl+Shift+A",
      "tags": ["work", "browser"],
      "favorite": true,
      "enabled": true,
      "steps": [
        {
          "type": "open_url",
          "params": {
            "url": "https://example.com"
          }
        }
      ]
    }
  ]
}
```

#### Action Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier |
| name | string | Yes | Display name |
| description | string | No | What the action does |
| hotkey | string | No | Global hotkey trigger |
| tags | array | No | Categorization tags |
| favorite | boolean | No | Show in quick actions |
| enabled | boolean | No | Whether action is active |
| steps | array | Yes | List of steps to execute |

---

### launchers.json

Stores launcher configurations (alternative format).

```json
{
  "config_version": 1,
  "launchers": [
    {
      "id": "work_setup",
      "name": "Work Setup",
      "description": "Opens all work applications",
      "hotkey": "Ctrl+Shift+W",
      "enabled": true,
      "schedule_time": null,
      "schedule_delay": null,
      "steps": [...]
    }
  ]
}
```

---

### templates.json

Stores text templates.

```json
{
  "config_version": 1,
  "templates": [
    {
      "id": "email_signature",
      "name": "Email Signature",
      "description": "My standard signature",
      "hotkey": "Ctrl+Shift+S",
      "content": "Best regards,\n{{ name }}\n{{ title }}",
      "variables": {
        "name": "John Doe",
        "title": "Software Engineer"
      }
    }
  ]
}
```

---

### settings.json

Stores app preferences.

```json
{
  "theme": "glass",
  "nav_position": "left",
  "start_minimized": false,
  "minimize_to_tray": true,
  "show_notifications": true
}
```

#### Settings Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| theme | string | "glass" | UI theme |
| nav_position | string | "left" | Sidebar position |
| start_minimized | boolean | false | Start in tray |
| minimize_to_tray | boolean | true | Minimize instead of close |
| show_notifications | boolean | true | Show tray notifications |

---

## 🔧 Step Configuration

### open_app
```json
{
  "type": "open_app",
  "params": {
    "path": "C:\\Program Files\\App\\app.exe"
  }
}
```

### open_url
```json
{
  "type": "open_url",
  "params": {
    "url": "https://example.com"
  }
}
```

### delay
```json
{
  "type": "delay",
  "params": {
    "seconds": 2.5
  }
}
```

### click
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
```json
{
  "type": "type_text",
  "params": {
    "text": "Hello World"
  }
}
```

### hotkey
```json
{
  "type": "hotkey",
  "params": {
    "keys": ["ctrl", "c"]
  }
}
```

### paste
```json
{
  "type": "paste",
  "params": {}
}
```

---

## 🎨 Theme Options

Available theme values:
- `productivity` - Professional blue
- `calm` - Relaxing green
- `contrast` - High contrast
- `playful` - Vibrant purple
- `glass` - Modern dark

---

## 📍 Nav Position Options

- `left` - Sidebar on left (default)
- `right` - Sidebar on right
- `top` - Navigation at top
- `bottom` - Navigation at bottom

---

## 🔐 Backup & Restore

### Backup
Copy the entire `.deskpilot` folder to a safe location.

### Restore
Replace the `.deskpilot` folder with your backup.

### Export Actions
1. Open Edit JSON tab
2. Copy the JSON content
3. Save to a file

### Import Actions
1. Open Edit JSON tab
2. Paste your JSON
3. Click Save

---

## ⚠️ Important Notes

1. **JSON Validation**: Invalid JSON will prevent the app from loading. Use the Edit JSON tab's Validate button.

2. **Unique IDs**: Each action must have a unique `id`. Duplicates will cause issues.

3. **Hotkey Conflicts**: Avoid hotkeys that conflict with Windows or other applications.

4. **Path Escaping**: In JSON, backslashes must be escaped: `C:\\Program Files\\...`

5. **File Permissions**: The config folder must be writable by your user account.

---

[← Back to README](../README.md)
