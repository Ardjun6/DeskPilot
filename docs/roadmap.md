# DeskPilot Product Roadmap (Draft)

This roadmap captures proposed product-level improvements and is intended as a planning aid
for future iterations. Items are grouped by theme and ordered by perceived ROI.

## 1. UX / Product-Level Improvements (highest ROI)

### 1.1 Command-first workflow (power-user mode)
- Global command palette hotkey (even when DeskPilot is closed/minimized).
- Allow quick intents:
  - `email` → opens email template flow.
  - `research topic` → runs browser workflow.
- Auto-fill last-used arguments.

**Why:** Turns DeskPilot into a launcher brain, not just an app.

### 1.2 Action chaining & “Quick Flows”
- Right-click an action → “Chain to…”.
- Create mini workflows without opening JSON.
- Visual “flow preview” (non-editable, read-only).

**Why:** Reduces JSON friction for daily users.

### 1.3 Smart defaults & learning behavior
- Remember:
  - Last app used for `open_app`.
  - Most used templates.
  - Preferred tone.
- Surface “Suggested actions” at the top.

**Why:** Makes DeskPilot feel intelligent without AI.

## 2. Macro & Automation Improvements

### 2.1 Step-by-step execution mode
- Toggle:
  - Run full macro.
  - Step through macro (Next / Skip / Stop).
- Highlight active step in UI.

**Why:** Debugging + trust.

### 2.2 Conditional logic in JSON (big upgrade)
Add:

```json
{
  "type": "if",
  "condition": "window_contains('Outlook')",
  "then": [...],
  "else": [...]
}
```

**Why:** Real workflows depend on state.

### 2.3 Variables memory
Let users choose:
- Prompt every time.
- Remember for session.
- Remember permanently.

**Why:** Cuts repeated prompts.

## 3. App Discovery & Icon System (advanced)

### 3.1 App tagging system
- Auto-tag apps:
  - browser, editor, mail, chat, dev, media.
- Allow user tags.

**Why:** Search becomes faster than raw names.

### 3.2 Icon normalization
- Normalize icons:
  - same size.
  - same padding.
  - same background mask (Claude-style).

**Why:** Visual polish matters a lot.

### 3.3 App health detection
- Detect broken shortcuts / moved executables.
- Show warning icon.
- Offer “Fix path”.

**Why:** Prevents silent failures.

## 4. JSON Editor (editor-grade features)

### 4.1 Schema-aware autocomplete
Autocomplete:
- Step types.
- Keys.
- Known apps.
- Tooltip docs per step.

**Why:** Makes JSON usable by non-developers.

### 4.2 Version history
- Auto-save versions:
  - `macros.json.bak.1`
  - `macros.json.bak.2`
- Restore previous version.

**Why:** Safety net for power users.

### 4.3 Diff view on save
Show:
- What changed.
- Before / after.
- Confirm save.

**Why:** Prevents accidental mistakes.

## 5. Action / Flow Engine Improvements

### 5.1 Deterministic execution
- Every step reports:
  - `started_at`
  - `ended_at`
  - `duration`
- Show execution timeline.

**Why:** Debugging + performance insights.

### 5.2 Retry & fallback

```json
{
  "type": "open_app",
  "path": "...",
  "retry": 2,
  "fallback": { "type": "notify", "message": "App not found" }
}
```

**Why:** Makes automations robust.

### 5.3 Sandbox mode
- Run actions in “safe sandbox”.
- No file deletion.
- No typing.

**Why:** Testing without fear.

## 6. UI / Visual Polish (Claude-level)

### 6.1 Micro-interactions
- Subtle:
  - button hover fades.
  - list selection slide.
  - modal entrance easing.

**Why:** Makes the app feel expensive.

### 6.2 Visual hierarchy tuning
- Different font weights:
  - title
  - secondary info
  - meta (hotkeys, tags)
- Muted text colors used consistently.

**Why:** Readability and calm.

### 6.3 Empty states with guidance
Instead of “No macros”:
- “Create your first macro”.
- Button → opens example JSON.

**Why:** Reduces cognitive load.

## 7. Performance & Stability

### 7.1 Lazy loading
- Load:
  - app icons on demand.
  - macros only when entering view.

**Why:** Faster startup.

### 7.2 Crash recovery
- On crash:
  - restore last state.
  - show “What happened” panel.

**Why:** Professional feel.

## 8. Advanced (next phase)

### 8.1 Plugin system (later)
- Drop-in Python files for custom steps.
- Explicit permission system.

**Why:** Community extensibility without chaos.

### 8.2 Import / export packs
- Export:
  - macros
  - templates
  - profiles
- Import on another machine.

**Why:** DeskPilot becomes portable.

### 8.3 Read-only “viewer mode”
- Share configs safely.
- No execution.

**Why:** Collaboration without risk.
