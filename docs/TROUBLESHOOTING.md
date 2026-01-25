# 🔧 Troubleshooting

Common issues and their solutions.

---

## 🚀 Startup Issues

### App won't start

**Symptoms:**
- Nothing happens when running
- Window appears then closes immediately

**Solutions:**
1. Check Python version (need 3.10+):
   ```powershell
   python --version
   ```

2. Verify dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run with error output:
   ```powershell
   python -m deskpilot.main 2>&1
   ```

---

### "Module not found" errors

**Solution:**
Make sure virtual environment is activated:
```powershell
.venv\Scripts\activate
```

Then reinstall:
```powershell
pip install -r requirements.txt
```

---

### "PyInstaller is required" message

**This is just a warning**, not an error. The app will still run. To remove it:
```powershell
python -m deskpilot.main --no-build-exe
```

Or install PyInstaller:
```powershell
pip install pyinstaller
```

---

### DPI/Scaling warnings

**Message:**
```
SetProcessDpiAwarenessContext() failed
```

**This is harmless.** It's a Qt warning about Windows DPI handling. The app works fine.

---

### "Unknown property cursor" warnings

**This is harmless.** Qt doesn't support CSS cursor properties. The app works fine.

---

## 🖱️ Action Issues

### Clicks happen at wrong position

**Causes:**
- Screen resolution changed
- Display scaling changed
- Multiple monitors

**Solutions:**
1. Re-record the action at current resolution
2. Use relative coordinates if possible
3. Add delays to let windows fully load

---

### Hotkey doesn't work

**Causes:**
- Hotkey conflict with another app
- App not running/minimized
- Action is disabled

**Solutions:**
1. Try a different hotkey combination
2. Check action is enabled (not grayed out)
3. Ensure DeskPilot is running (check system tray)
4. Restart DeskPilot

---

### Action runs too fast

**Solution:**
Add delay steps between actions:
```json
{
  "type": "delay",
  "params": {"seconds": 1}
}
```

---

### Typed text has wrong characters

**Causes:**
- Keyboard layout mismatch
- Special characters

**Solution:**
Use paste instead of type_text:
1. Copy text to clipboard
2. Use paste step

---

## 🎬 Recorder Issues

### Recording doesn't capture anything

**Solutions:**
1. Make sure checkboxes are enabled (Record mouse/keyboard)
2. Run as Administrator (some apps block input capture)
3. Check pynput is installed:
   ```powershell
   pip install pynput
   ```

---

### Recorded clicks are offset

**Cause:** Screen scaling

**Solution:** Record at 100% display scaling, or adjust coordinates after recording.

---

## 📋 Clipboard Issues

### Clipboard history not working

**Solutions:**
1. Restart DeskPilot
2. Check if other clipboard managers are conflicting
3. Verify pyperclip is installed:
   ```powershell
   pip install pyperclip
   ```

---

### Ctrl+Shift+V not working

**Cause:** Hotkey conflict

**Solution:** Use the toolbar 📋 button or tray menu instead.

---

## 🖱️ Jiggle Issues

### Mouse not moving

**Solutions:**
1. Make sure "Start" was clicked
2. Try a visible pattern (not "Invisible")
3. Check interval isn't too long
4. Verify pyautogui is working:
   ```python
   import pyautogui
   pyautogui.moveRel(5, 0)
   ```

---

### Jiggle doesn't prevent sleep

**Solutions:**
1. Try Caffeine Mode
2. Reduce interval (e.g., 10 seconds)
3. Check Windows power settings
4. Some corporate policies override this

---

### Schedule not starting

**Solutions:**
1. Verify "Auto start/stop" is checked
2. Check times are set correctly
3. Verify correct days are selected
4. Make sure DeskPilot is running at the scheduled time

---

## 🎨 UI Issues

### Theme not applying

**Solution:**
1. Restart DeskPilot
2. Try a different theme first, then switch back

---

### Sidebar disappeared

**Solutions:**
1. Change Nav position in settings
2. Restart DeskPilot
3. Delete settings.json and restart

---

### Window too small/large

**Solution:**
Resize the window - DeskPilot remembers window size.

---

### System tray icon missing

**Solutions:**
1. Check system tray overflow (^ arrow)
2. Right-click taskbar → Taskbar settings → Turn on DeskPilot
3. Restart DeskPilot

---

## 💾 Configuration Issues

### Settings not saving

**Solutions:**
1. Check write permissions on config folder
2. Run as Administrator once
3. Delete config folder and let it recreate:
   ```powershell
   Remove-Item -Recurse ~\.deskpilot
   ```

---

### Invalid JSON error

**Solutions:**
1. Use Edit JSON tab's "Validate JSON" button
2. Check for:
   - Missing commas
   - Missing quotes
   - Unescaped backslashes (use `\\`)
   - Trailing commas (not allowed in JSON)

---

### Actions disappeared

**Causes:**
- Corrupted actions.json
- Accidentally deleted

**Solutions:**
1. Check for backup in config folder
2. Restore from your own backup
3. Recreate actions

---

## 🔄 Performance Issues

### App is slow

**Solutions:**
1. Reduce clipboard history size
2. Disable unused features
3. Close and reopen the app
4. Check for runaway processes in Task Manager

---

### High CPU usage

**Causes:**
- Jiggle running with very short interval
- Clipboard polling too fast

**Solutions:**
1. Increase jiggle interval (30+ seconds)
2. Restart DeskPilot

---

## 🆘 Getting More Help

### Enable debug logging
```powershell
python -m deskpilot.main --theme glass 2>&1 | Out-File debug.log
```

### Report a bug
Include:
1. Windows version
2. Python version
3. Error message
4. Steps to reproduce
5. Contents of debug.log

---

## 🔄 Reset Everything

Nuclear option - completely reset DeskPilot:

```powershell
# Remove all configuration
Remove-Item -Recurse ~\.deskpilot

# Reinstall dependencies
pip uninstall -y PySide6 pyautogui pynput keyboard
pip install -r requirements.txt

# Run fresh
python -m deskpilot.main
```

---

[← Back to README](../README.md)
