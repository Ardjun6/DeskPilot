from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...actions.engine import ActionEngine
from ...config.config_manager import ConfigManager
from ...utils.hotkeys import validate_hotkey
from ..json_editor import JsonEditorDialog
from ..widgets.action_list import ActionList


class ActionView(QWidget):
    """Action list view with run/preview signals, sorting, and Active/Inactive status."""

    run_requested = Signal(str)
    preview_requested = Signal(str)

    def __init__(
        self,
        config_manager: ConfigManager,
        action_engine: ActionEngine,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.action_engine = action_engine
        self.current_sort = "name"
        self.current_filter = "all"

        self._build_ui()
        self._connect_signals()
        self.refresh()

    def _build_ui(self) -> None:
        self.list_widget = ActionList()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(4, 4, 4, 4)
        container_layout.addWidget(self.list_widget)
        scroll.setWidget(container)
        self.scroll = scroll

        # Better empty state
        self.empty_widget = QWidget()
        self.empty_widget.setObjectName("EmptyState")
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(16)
        
        empty_icon = QLabel("📭")
        empty_icon.setObjectName("EmptyStateIcon")
        empty_icon.setStyleSheet("font-size: 64px;")
        empty_icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_icon)
        
        empty_title = QLabel("No Actions Yet")
        empty_title.setObjectName("EmptyStateTitle")
        empty_title.setStyleSheet("font-size: 20px; font-weight: 600;")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_title)
        
        empty_desc = QLabel("Create your first automation using the Workflow Builder\nor Recorder tab, or add actions via Edit JSON.")
        empty_desc.setObjectName("EmptyStateDesc")
        empty_desc.setStyleSheet("font-size: 13px; color: #888;")
        empty_desc.setAlignment(Qt.AlignCenter)
        empty_desc.setWordWrap(True)
        empty_layout.addWidget(empty_desc)
        
        # Quick action buttons in empty state
        empty_buttons = QHBoxLayout()
        empty_buttons.setAlignment(Qt.AlignCenter)
        empty_buttons.setSpacing(12)
        
        workflow_btn = QPushButton("🔧 Open Workflow Builder")
        workflow_btn.setProperty("primary", True)
        workflow_btn.clicked.connect(lambda: self._go_to_tab(2))
        empty_buttons.addWidget(workflow_btn)
        
        recorder_btn = QPushButton("🎬 Open Recorder")
        recorder_btn.clicked.connect(lambda: self._go_to_tab(3))
        empty_buttons.addWidget(recorder_btn)
        
        empty_layout.addLayout(empty_buttons)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("⚡ Actions & Launchers")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)
        
        # Filter and sort controls
        controls = QHBoxLayout()
        controls.setSpacing(12)
        
        controls.addWidget(QLabel("Show:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Favorites"])
        controls.addWidget(self.filter_combo)
        
        controls.addWidget(QLabel("Sort:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name (A-Z)", "Name (Z-A)", "Favorites First"])
        controls.addWidget(self.sort_combo)
        
        controls.addStretch()
        
        self.edit_btn = QPushButton("📄 Edit actions.json")
        controls.addWidget(self.edit_btn)
        
        main_layout.addLayout(controls)
        
        # Content (scroll or empty)
        main_layout.addWidget(scroll, 1)
        main_layout.addWidget(self.empty_widget, 1)
    
    def _go_to_tab(self, index: int) -> None:
        """Navigate to another tab."""
        main = self.window()
        if hasattr(main, 'stack') and hasattr(main, 'sidebar'):
            main.stack.setCurrentIndex(index)
            main.sidebar.select_index(index)

    def _connect_signals(self) -> None:
        self.list_widget.run_requested.connect(self._emit_run)
        self.list_widget.preview_requested.connect(self._emit_preview)
        self.list_widget.hotkey_requested.connect(self._set_hotkey)
        self.list_widget.edit_requested.connect(self._open_editor)
        self.list_widget.delete_requested.connect(self._delete_action)
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        self.edit_btn.clicked.connect(self._open_json_editor)

    def _on_filter_changed(self, text: str) -> None:
        filter_map = {
            "All": "all",
            "Favorites": "favorites",
        }
        self.current_filter = filter_map.get(text, "all")
        self.refresh()

    def _on_sort_changed(self, text: str) -> None:
        sort_map = {
            "Name (A-Z)": "name_asc",
            "Name (Z-A)": "name_desc",
            "Favorites First": "favorites",
        }
        self.current_sort = sort_map.get(text, "name_asc")
        self.refresh()

    def refresh(self) -> None:
        all_actions = self.action_engine.list_actions()
        
        # Apply filter
        if self.current_filter == "favorites":
            all_actions = [a for a in all_actions if a.favorite]
        
        # Apply sort
        if self.current_sort == "name_asc":
            all_actions = sorted(all_actions, key=lambda a: a.name.lower())
        elif self.current_sort == "name_desc":
            all_actions = sorted(all_actions, key=lambda a: a.name.lower(), reverse=True)
        elif self.current_sort == "favorites":
            all_actions = sorted(all_actions, key=lambda a: (not a.favorite, a.name.lower()))
        
        actions = [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "favorite": a.favorite,
                "tags": a.tags,
                "hotkey": a.hotkey,
                "enabled": a.enabled,
            }
            for a in all_actions
        ]
        
        if not actions:
            self.list_widget.hide()
            self.scroll.hide()
            self.empty_widget.show()
        else:
            self.empty_widget.hide()
            self.scroll.show()
            self.list_widget.show()
            self.list_widget.set_actions(actions)

    def filter_items(self, text: str) -> None:
        text_lower = text.lower()
        all_actions = self.action_engine.list_actions()
        
        filtered = [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "favorite": a.favorite,
                "tags": a.tags,
                "hotkey": a.hotkey,
                "enabled": a.enabled,
            }
            for a in all_actions
            if text_lower in a.name.lower()
            or text_lower in a.description.lower()
            or any(text_lower in t.lower() for t in a.tags)
        ]
        self.list_widget.set_actions(filtered)

    def _emit_run(self, action_id: str) -> None:
        self.run_requested.emit(action_id)

    def _emit_preview(self, action_id: str) -> None:
        self.preview_requested.emit(action_id)

    def _open_json_editor(self) -> None:
        dialog = JsonEditorDialog(
            path=self.config_manager.actions_path,
            loader=lambda text: self.config_manager.actions.model_validate_json(text),
            formatter=lambda data: self.config_manager.actions.model_validate(data).model_dump(),
            parent=self,
        )
        dialog.exec()
        self.config_manager.actions = dialog.reload_model(self.config_manager.actions_path, self.config_manager.actions)
        self.refresh()
        self._refresh_hotkeys()

    def _open_editor(self, action_id: str) -> None:
        """Open workflow builder to edit this action."""
        action = self.action_engine.get_action(action_id)
        if action is None:
            return
        
        # Navigate to workflow builder tab and load the action
        main = self.window()
        if hasattr(main, 'stack') and hasattr(main, 'sidebar') and hasattr(main, 'workflow_view'):
            # Load action into workflow builder
            main.workflow_view.load_action(action)
            # Switch to workflow builder tab (index 2)
            main.stack.setCurrentIndex(2)
            main.sidebar.select_index(2)

    def _set_hotkey(self, action_id: str) -> None:
        action = self.action_engine.get_action(action_id)
        if action is None:
            return
        hotkey, ok = self._prompt_text("Set hotkey", "Hotkey (e.g., Ctrl+K or H+P):", action.hotkey or "")
        if not ok:
            return
        is_valid, normalized, error = validate_hotkey(hotkey)
        if not is_valid:
            QMessageBox.warning(self, "Invalid hotkey", f"Hotkey couldn't be registered: {error}")
            return
        action.hotkey = normalized or None
        self.config_manager.save_all()
        self.refresh()
        self._refresh_hotkeys()

    def _prompt_text(self, title: str, label: str, initial: str = "") -> tuple[str, bool]:
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        edit = QLineEdit()
        edit.setText(initial)
        lbl = QLabel(label)
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        hl = QHBoxLayout()
        hl.addWidget(btn_ok)
        hl.addWidget(btn_cancel)
        layout = QVBoxLayout(dlg)
        layout.addWidget(lbl)
        layout.addWidget(edit)
        layout.addLayout(hl)

        chosen = {"ok": False}

        def accept() -> None:
            chosen["ok"] = True
            dlg.accept()

        btn_ok.clicked.connect(accept)
        btn_cancel.clicked.connect(dlg.reject)
        dlg.exec()
        return edit.text().strip(), chosen["ok"]

    def _delete_action(self, action_id: str) -> None:
        action = self.action_engine.get_action(action_id)
        if action is None:
            return
        confirm = QMessageBox.question(
            self,
            "Delete action",
            f"Delete '{action.name}'? This will remove it from actions.json.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        self.config_manager.actions.actions = [
            existing for existing in self.config_manager.actions.actions if existing.id != action_id
        ]
        self.config_manager.save_all()
        self.refresh()

    def _refresh_hotkeys(self) -> None:
        main = self.window()
        if hasattr(main, "refresh_hotkeys"):
            main.refresh_hotkeys()
