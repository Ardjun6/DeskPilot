"""System tray integration for DeskPilot."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable

from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

if TYPE_CHECKING:
    from .main_window import MainWindow


class SystemTrayManager(QObject):
    """Manages system tray icon and menu."""

    show_requested = Signal()
    quit_requested = Signal()
    action_triggered = Signal(str)  # action_id

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.tray_menu: Optional[QMenu] = None
        self.quick_actions_menu: Optional[QMenu] = None
        self.jiggle_action: Optional[QAction] = None
        self.main_window: Optional["MainWindow"] = None
        self._action_callbacks: dict[str, Callable] = {}
        self._initialized = False

    def setup(self, main_window: "MainWindow") -> None:
        """Initialize the system tray."""
        self.main_window = main_window
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(main_window)
        
        # Use a standard icon
        from PySide6.QtWidgets import QStyle
        app = QApplication.instance()
        if app:
            self.tray_icon.setIcon(app.style().standardIcon(QStyle.SP_DesktopIcon))
        
        self.tray_icon.setToolTip("DeskPilot - Desktop Automation")
        
        # Create menu
        self._build_menu()
        
        # Connect signals
        self.tray_icon.activated.connect(self._on_activated)
        
        # Show tray icon
        self.tray_icon.show()
        self._initialized = True

    def _build_menu(self) -> None:
        """Build the tray context menu."""
        self.tray_menu = QMenu()
        
        # Show/Hide action
        show_action = QAction("Show DeskPilot", self.tray_menu)
        show_action.triggered.connect(self._show_main_window)
        self.tray_menu.addAction(show_action)
        
        self.tray_menu.addSeparator()
        
        # Quick Actions submenu
        self.quick_actions_menu = self.tray_menu.addMenu("⚡ Quick Actions")
        self._populate_quick_actions()
        
        # Jiggle toggle
        self.jiggle_action = QAction("🖱️ Start Jiggle", self.tray_menu)
        self.jiggle_action.triggered.connect(self._toggle_jiggle)
        self.tray_menu.addAction(self.jiggle_action)
        
        # Clipboard action
        clipboard_action = QAction("📋 Clipboard History", self.tray_menu)
        clipboard_action.triggered.connect(self._show_clipboard)
        self.tray_menu.addAction(clipboard_action)
        
        # Quick widget
        widget_action = QAction("📌 Quick Actions Widget", self.tray_menu)
        widget_action.triggered.connect(self._show_quick_widget)
        self.tray_menu.addAction(widget_action)
        
        self.tray_menu.addSeparator()
        
        # Settings
        settings_action = QAction("⚙️ Settings", self.tray_menu)
        settings_action.triggered.connect(self._show_settings)
        self.tray_menu.addAction(settings_action)
        
        self.tray_menu.addSeparator()
        
        # Quit
        quit_action = QAction("❌ Quit", self.tray_menu)
        quit_action.triggered.connect(self._quit_app)
        self.tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)

    def _populate_quick_actions(self) -> None:
        """Populate quick actions from favorites."""
        self.quick_actions_menu.clear()
        
        if self.main_window is None:
            return
        
        # Get favorite actions
        actions = self.main_window.action_engine.list_actions()
        favorites = [a for a in actions if a.favorite][:10]  # Max 10
        
        if not favorites:
            # Show all actions if no favorites
            favorites = actions[:10]
        
        for action in favorites:
            menu_action = QAction(f"▶ {action.name}", self.quick_actions_menu)
            menu_action.triggered.connect(
                lambda checked, aid=action.id: self._run_action(aid)
            )
            self.quick_actions_menu.addAction(menu_action)
        
        if not favorites:
            empty_action = QAction("(No actions)", self.quick_actions_menu)
            empty_action.setEnabled(False)
            self.quick_actions_menu.addAction(empty_action)

    def refresh_actions(self) -> None:
        """Refresh the quick actions menu."""
        if self._initialized and self.quick_actions_menu:
            self._populate_quick_actions()

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_main_window()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click - show menu on some platforms
            pass

    def _show_main_window(self) -> None:
        """Show and raise the main window."""
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()

    def _run_action(self, action_id: str) -> None:
        """Run an action from tray menu."""
        if self.main_window:
            self.main_window._run_action(action_id)

    def _toggle_jiggle(self) -> None:
        """Toggle jiggle on/off."""
        if self.main_window and hasattr(self.main_window, 'jiggle_view'):
            jiggle = self.main_window.jiggle_view
            if jiggle.is_running:
                jiggle._stop_jiggling()
                self.jiggle_action.setText("🖱️ Start Jiggle")
                self.update_tooltip("DeskPilot - Desktop Automation")
            else:
                jiggle._start_jiggling()
                self.jiggle_action.setText("🖱️ Stop Jiggle")
                self.update_tooltip("DeskPilot - Jiggle Active 🖱️")

    def _show_clipboard(self) -> None:
        """Show clipboard history."""
        if self.main_window and hasattr(self.main_window, 'clipboard_manager'):
            self.main_window.clipboard_manager.show_popup()

    def _show_quick_widget(self) -> None:
        """Show the quick actions floating widget."""
        if self.main_window and hasattr(self.main_window, 'quick_widget'):
            self.main_window.quick_widget.show()
            self.main_window.quick_widget.raise_()

    def _show_settings(self) -> None:
        """Show settings view."""
        self._show_main_window()
        if self.main_window:
            # Switch to settings tab (index 4)
            self.main_window.stack.setCurrentIndex(4)
            self.main_window.sidebar.setCurrentRow(4)

    def _quit_app(self) -> None:
        """Quit the application."""
        if self.main_window:
            # Stop jiggle if running
            if hasattr(self.main_window, 'jiggle_view'):
                self.main_window.jiggle_view._stop_jiggling()
        
        QApplication.quit()

    def update_tooltip(self, text: str) -> None:
        """Update tray icon tooltip."""
        if self.tray_icon:
            self.tray_icon.setToolTip(text)

    def show_notification(self, title: str, message: str, duration: int = 3000) -> None:
        """Show a system notification."""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, duration)

    def hide(self) -> None:
        """Hide the tray icon."""
        if self.tray_icon:
            self.tray_icon.hide()
