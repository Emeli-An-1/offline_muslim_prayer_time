"""
PrayerOffline - Main Entry Point (FIXED)
Properly integrated with all services and views
"""

import flet as ft
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging FIRST
log_file = project_root / 'prayer_offline.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import app class
from app import PrayerOfflineApp


def main(page: ft.Page):
    """Main entry point for Flet application"""
    try:
        logger.info("Starting PrayerOffline...")

        # Import StorageService first
        from services.storage import StorageService

        # Initialize storage
        storage = StorageService()
        logger.info("Storage initialized")

        # Create and initialize app
        app = PrayerOfflineApp(page, storage)
        app.initialize()

        logger.info("PrayerOffline started successfully")

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)

        # Show error to user
        error_view = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.ERROR),
                    ft.Text(
                        "Failed to Start Application",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        str(e),
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        f"Check log file: {log_file}",
                        size=12,
                        italic=True,
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=40,
        )

        page.add(error_view)
        page.update()


if __name__ == '__main__':
    try:
        logger.info("Launching PrayerOffline...")
        ft.app(target=main, name="PrayerOffline")
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Startup error: {e}", exc_info=True)
        print(f"\nFailed to start PrayerOffline: {e}")
        print(f"Check log file: {log_file}")
        sys.exit(1)