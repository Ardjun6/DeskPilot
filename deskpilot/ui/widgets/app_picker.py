"""
Application Picker Dialog - Scans installed apps with loading animation.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QWidget,
    QApplication,
)


class AppScannerThread(QThread):
    """Background thread to scan for installed applications."""
    
    apps_found = Signal(list)  # List of (name, path) tuples
    progress = Signal(str)     # Status message
    
    def run(self):
        apps = []
        
        if sys.platform == "win32":
            apps = self._scan_windows()
        elif sys.platform == "darwin":
            apps = self._scan_macos()
        else:
            apps = self._scan_linux()
        
        # Sort by name
        apps.sort(key=lambda x: x[0].lower())
        self.apps_found.emit(apps)
    
    def _scan_windows(self) -> List[Tuple[str, str]]:
        apps = []
        
        # Common system apps
        self.progress.emit("Scanning system apps...")
        system_apps = [
            ("Notepad", "notepad.exe"),
            ("Calculator", "calc.exe"),
            ("Paint", "mspaint.exe"),
            ("Command Prompt", "cmd.exe"),
            ("PowerShell", "powershell.exe"),
            ("File Explorer", "explorer.exe"),
            ("Task Manager", "taskmgr.exe"),
            ("Control Panel", "control.exe"),
            ("Snipping Tool", "SnippingTool.exe"),
            ("WordPad", "write.exe"),
            ("Windows Terminal", "wt.exe"),
        ]
        apps.extend(system_apps)
        
        # Scan Program Files
        program_dirs = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
            os.environ.get("LOCALAPPDATA", ""),
        ]
        
        for prog_dir in program_dirs:
            if prog_dir and os.path.exists(prog_dir):
                self.progress.emit(f"Scanning {Path(prog_dir).name}...")
                apps.extend(self._scan_directory(prog_dir, max_depth=3))
        
        # Scan Start Menu shortcuts
        start_menu_dirs = [
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft", "Windows", "Start Menu", "Programs"),
        ]
        
        for sm_dir in start_menu_dirs:
            if os.path.exists(sm_dir):
                self.progress.emit("Scanning Start Menu...")
                apps.extend(self._scan_shortcuts(sm_dir))
        
        # Remove duplicates (by path)
        seen_paths = set()
        unique_apps = []
        for name, path in apps:
            path_lower = path.lower()
            if path_lower not in seen_paths:
                seen_paths.add(path_lower)
                unique_apps.append((name, path))
        
        return unique_apps
    
    def _scan_directory(self, base_dir: str, max_depth: int = 2) -> List[Tuple[str, str]]:
        """Scan directory for .exe files."""
        apps = []
        
        try:
            for root, dirs, files in os.walk(base_dir):
                # Check depth
                depth = root[len(base_dir):].count(os.sep)
                if depth >= max_depth:
                    dirs.clear()
                    continue
                
                # Skip certain directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in 
                          ('cache', 'temp', 'logs', 'data', 'resources', 'locales', 'node_modules')]
                
                for f in files:
                    if f.lower().endswith('.exe'):
                        # Skip installer/uninstaller/updater executables
                        lower_name = f.lower()
                        if any(skip in lower_name for skip in 
                               ['unins', 'setup', 'install', 'update', 'crash', 'helper', 'service']):
                            continue
                        
                        full_path = os.path.join(root, f)
                        app_name = f[:-4]  # Remove .exe
                        
                        # Clean up name
                        app_name = app_name.replace('-', ' ').replace('_', ' ')
                        if app_name:
                            apps.append((app_name, full_path))
        except (PermissionError, OSError):
            pass
        
        return apps
    
    def _scan_shortcuts(self, base_dir: str) -> List[Tuple[str, str]]:
        """Scan for .lnk shortcuts and resolve them."""
        apps = []
        
        try:
            import subprocess
            
            for root, dirs, files in os.walk(base_dir):
                for f in files:
                    if f.lower().endswith('.lnk'):
                        lnk_path = os.path.join(root, f)
                        app_name = f[:-4]  # Remove .lnk
                        
                        # Try to resolve shortcut using PowerShell
                        try:
                            result = subprocess.run(
                                ['powershell', '-Command', 
                                 f'(New-Object -ComObject WScript.Shell).CreateShortcut("{lnk_path}").TargetPath'],
                                capture_output=True,
                                text=True,
                                timeout=2
                            )
                            target = result.stdout.strip()
                            if target and os.path.exists(target) and target.lower().endswith('.exe'):
                                apps.append((app_name, target))
                        except:
                            pass
        except (PermissionError, OSError):
            pass
        
        return apps
    
    def _scan_macos(self) -> List[Tuple[str, str]]:
        apps = []
        app_dirs = ["/Applications", os.path.expanduser("~/Applications")]
        
        for app_dir in app_dirs:
            if os.path.exists(app_dir):
                try:
                    for item in os.listdir(app_dir):
                        if item.endswith('.app'):
                            name = item[:-4]
                            path = os.path.join(app_dir, item)
                            apps.append((name, path))
                except (PermissionError, OSError):
                    pass
        
        return apps
    
    def _scan_linux(self) -> List[Tuple[str, str]]:
        apps = []
        
        # Check common binary locations
        bin_dirs = ["/usr/bin", "/usr/local/bin", os.path.expanduser("~/.local/bin")]
        desktop_dirs = [
            "/usr/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]
        
        # Scan .desktop files for GUI apps
        for desktop_dir in desktop_dirs:
            if os.path.exists(desktop_dir):
                try:
                    for f in os.listdir(desktop_dir):
                        if f.endswith('.desktop'):
                            path = os.path.join(desktop_dir, f)
                            name, exec_path = self._parse_desktop_file(path)
                            if name and exec_path:
                                apps.append((name, exec_path))
                except (PermissionError, OSError):
                    pass
        
        return apps
    
    def _parse_desktop_file(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse a .desktop file to get name and executable."""
        name = None
        exec_path = None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('Name=') and not name:
                        name = line[5:].strip()
                    elif line.startswith('Exec='):
                        exec_path = line[5:].strip().split()[0]
        except:
            pass
        
        return name, exec_path


class AppPickerDialog(QDialog):
    """Dialog to select an installed application."""
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Application")
        self.setMinimumSize(500, 550)
        self.setModal(True)
        
        self._all_apps: List[Tuple[str, str]] = []
        self._selected_app: Optional[Tuple[str, str]] = None
        
        self._build_ui()
        self._start_scan()
    
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title = QLabel("🖥️ Select Application")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)
        
        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search applications...")
        self.search.textChanged.connect(self._filter_apps)
        layout.addWidget(self.search)
        
        # Loading indicator
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.setAlignment(Qt.AlignCenter)
        
        self.loading_label = QLabel("⏳ Scanning applications...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 14px; padding: 40px;")
        loading_layout.addWidget(self.loading_label)
        
        self.loading_dots = ""
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self._animate_loading)
        
        layout.addWidget(self.loading_widget)
        
        # App list
        self.app_list = QListWidget()
        self.app_list.setStyleSheet("""
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background: #3b9eff;
            }
            QListWidget::item:hover:!selected {
                background: #252d3a;
            }
        """)
        self.app_list.itemDoubleClicked.connect(self._select_and_accept)
        self.app_list.hide()
        layout.addWidget(self.app_list, 1)
        
        # Manual path entry
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("Or enter path:"))
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("C:\\Path\\To\\Application.exe")
        manual_layout.addWidget(self.path_input, 1)
        
        browse_btn = QPushButton("📂 Browse")
        browse_btn.clicked.connect(self._browse_file)
        manual_layout.addWidget(browse_btn)
        
        layout.addLayout(manual_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        self.select_btn = QPushButton("Select")
        self.select_btn.setProperty("primary", True)
        self.select_btn.clicked.connect(self._accept_selection)
        btn_layout.addWidget(self.select_btn)
        
        layout.addLayout(btn_layout)
    
    def _start_scan(self) -> None:
        """Start scanning for apps in background."""
        self.loading_timer.start(300)
        
        self.scanner = AppScannerThread()
        self.scanner.apps_found.connect(self._on_apps_found)
        self.scanner.progress.connect(self._on_progress)
        self.scanner.start()
    
    def _animate_loading(self) -> None:
        """Animate the loading text."""
        self.loading_dots = (self.loading_dots + ".") if len(self.loading_dots) < 3 else ""
        self.loading_label.setText(f"⏳ Scanning applications{self.loading_dots}")
    
    def _on_progress(self, message: str) -> None:
        """Update progress message."""
        self.loading_label.setText(f"⏳ {message}")
    
    def _on_apps_found(self, apps: List[Tuple[str, str]]) -> None:
        """Called when app scanning is complete."""
        self.loading_timer.stop()
        self.loading_widget.hide()
        self.app_list.show()
        
        self._all_apps = apps
        self._populate_list(apps)
    
    def _populate_list(self, apps: List[Tuple[str, str]]) -> None:
        """Populate the app list."""
        self.app_list.clear()
        
        for name, path in apps:
            item = QListWidgetItem(f"📦 {name}")
            item.setData(Qt.UserRole, (name, path))
            item.setToolTip(path)
            self.app_list.addItem(item)
        
        # Show count
        if apps:
            self.search.setPlaceholderText(f"🔍 Search {len(apps)} applications...")
    
    def _filter_apps(self, text: str) -> None:
        """Filter the app list."""
        text = text.lower()
        
        if not text:
            self._populate_list(self._all_apps)
            return
        
        filtered = [
            (name, path) for name, path in self._all_apps
            if text in name.lower() or text in path.lower()
        ]
        self._populate_list(filtered)
    
    def _browse_file(self) -> None:
        """Open file browser."""
        if sys.platform == "win32":
            file_filter = "Executables (*.exe);;All Files (*.*)"
        elif sys.platform == "darwin":
            file_filter = "Applications (*.app);;All Files (*.*)"
        else:
            file_filter = "All Files (*.*)"
        
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application",
            "",
            file_filter
        )
        
        if path:
            self.path_input.setText(path)
    
    def _select_and_accept(self, item: QListWidgetItem) -> None:
        """Double-click to select and accept."""
        self._selected_app = item.data(Qt.UserRole)
        self.accept()
    
    def _accept_selection(self) -> None:
        """Accept the current selection."""
        # Check manual path first
        manual_path = self.path_input.text().strip()
        if manual_path:
            name = Path(manual_path).stem
            self._selected_app = (name, manual_path)
            self.accept()
            return
        
        # Check list selection
        item = self.app_list.currentItem()
        if item:
            self._selected_app = item.data(Qt.UserRole)
            self.accept()
    
    def get_selected(self) -> Optional[Tuple[str, str]]:
        """Get the selected app (name, path) or None."""
        return self._selected_app
    
    @staticmethod
    def get_app(parent=None) -> Optional[Tuple[str, str]]:
        """Static method to show dialog and get result."""
        dialog = AppPickerDialog(parent)
        if dialog.exec() == QDialog.Accepted:
            return dialog.get_selected()
        return None
