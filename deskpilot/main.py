"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           DESKPILOT - MAIN ENTRY POINT                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  This is where the app starts. Run with: python -m deskpilot.main            ║
║                                                                              ║
║  COMMAND LINE OPTIONS:                                                       ║
║    --theme <name>    Set theme (productivity, calm, contrast, playful, glass)║
║    --no-splash       Skip the splash screen                                  ║
║    --build-exe       Build standalone executable                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from PySide6.QtWidgets import QApplication

# ============================================================================
# IMPORTS FROM OTHER MODULES
# ============================================================================
from .app import DeskPilotApp                    # Main application class
from .ui.theme_manager import ThemeManager       # Handles colors/styling
from .ui.splash_screen import SplashScreen       # Startup animation


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments with theme, splash, and build options
    """
    parser = argparse.ArgumentParser(
        description="DeskPilot - Desktop Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m deskpilot.main                    # Run with defaults
  python -m deskpilot.main --theme glass      # Use glass theme
  python -m deskpilot.main --no-splash        # Skip splash screen
        """
    )
    
    parser.add_argument(
        "--theme",
        choices=["productivity", "calm", "contrast", "playful", "glass"],
        default="glass",
        help="UI theme to use (default: glass)"
    )
    
    parser.add_argument(
        "--no-splash",
        action="store_true",
        help="Skip the splash screen on startup"
    )
    
    parser.add_argument(
        "--build-exe",
        action="store_true", 
        help="Build standalone executable using PyInstaller"
    )
    
    return parser.parse_args()


def check_pyinstaller() -> bool:
    """Check if PyInstaller is available for building executables."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def main() -> int:
    """
    Main entry point for DeskPilot.
    
    This function:
    1. Parses command line arguments
    2. Creates the Qt application
    3. Sets up theming
    4. Shows splash screen (optional)
    5. Creates and shows the main window
    6. Starts the event loop
    
    Returns:
        Exit code (0 = success)
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Handle --build-exe flag
    if args.build_exe:
        if not check_pyinstaller():
            print("PyInstaller is required. Install with: pip install pyinstaller")
        else:
            from .build import build_executable
            build_executable()
        return 0
    
    # ========================================================================
    # CREATE QT APPLICATION
    # ========================================================================
    # QApplication must be created before any widgets
    app = QApplication(sys.argv)
    app.setApplicationName("DeskPilot")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DeskPilot")
    
    # High DPI is now automatic in Qt6, no need to set attributes
    
    # ========================================================================
    # SETUP THEME MANAGER
    # ========================================================================
    # ThemeManager controls all colors and styling
    # To change themes: Go to deskpilot/ui/theme_manager.py
    theme_manager = ThemeManager()
    theme_manager.set_theme(args.theme)
    
    # ========================================================================
    # SHOW SPLASH SCREEN (Optional)
    # ========================================================================
    splash: Optional[SplashScreen] = None
    if not args.no_splash:
        # Pass the colors dictionary, not the theme_manager object
        splash = SplashScreen(theme_manager.current.colors)
        splash.show()
        app.processEvents()  # Let splash render
    
    # ========================================================================
    # CREATE MAIN APPLICATION
    # ========================================================================
    # DeskPilotApp creates the main window and all components
    deskpilot = DeskPilotApp(app, theme_manager=theme_manager)
    
    # Close splash and show main window
    if splash:
        splash.close()
    
    deskpilot.main_window.show()
    
    # ========================================================================
    # START EVENT LOOP
    # ========================================================================
    # This runs until the user quits the application
    return app.exec()


# ============================================================================
# RUN THE APP
# ============================================================================
if __name__ == "__main__":
    sys.exit(main())
