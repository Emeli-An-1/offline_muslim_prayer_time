"""
Add this method to your SettingsView class
Place it after _create_app_section() method
"""

def _create_save_section(self) -> ft.Container:
    """Create save/reset buttons section"""
    
    def on_save_click(e):
        """Handle save button click"""
        try:
            # Save all settings
            self._save_settings()
            self._save_jamaat_config()
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN),
                        ft.Text("All settings saved successfully!", size=16)
                    ],
                    spacing=8
                ),
                bgcolor=ft.colors.GREEN_100
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            logger.info("All settings saved via Save button")
            
        except Exception as ex:
            logger.error(f"Failed to save settings: {ex}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.ERROR, color=ft.colors.RED),
                        ft.Text("Failed to save settings", size=16)
                    ],
                    spacing=8
                ),
                bgcolor=ft.colors.RED_100
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def on_reset_click(e):
        """Handle reset button click"""
        # Show confirmation dialog
        def close_dialog(dlg):
            dlg.open = False
            self.page.update()
        
        def confirm_reset(dlg):
            try:
                # Reset to defaults
                self.settings = self._load_settings()
                self.jamaat_configs = self._load_jamaat_config()
                
                # Clear storage and reload defaults
                default_settings = {
                    "location": {"lat": 40.7128, "lng": -74.0060, "city": "New York", "timezone": "America/New_York"},
                    "calculation_method": "ISNA",
                    "asr_school": "STANDARD",
                    "high_latitude_rule": "ANGLE_BASED",
                    "theme_mode": "System",
                    "theme_name": "islamic_prayer",
                    "language": "en",
                    "font_size": 14,
                    "notifications_enabled": True,
                    "vibration_enabled": True,
                    "sound_enabled": True,
                    "notification_sound": "default",
                    "data_retention_days": 90
                }
                
                self.storage.set("settings", default_settings)
                self.settings = default_settings
                
                close_dialog(dlg)
                
                # Rebuild the view
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Settings reset to defaults. Please restart app.")
                )
                self.page.snack_bar.open = True
                self.page.update()
                
                logger.info("Settings reset to defaults")
                
            except Exception as ex:
                logger.error(f"Failed to reset settings: {ex}")
                close_dialog(dlg)
        
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Reset Settings?"),
            content=ft.Column(
                controls=[
                    ft.Text("This will reset ALL settings to default values."),
                    ft.Text("This action cannot be undone.", color=ft.colors.ERROR, weight=ft.FontWeight.BOLD)
                ],
                tight=True,
                spacing=8
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda x: close_dialog(confirm_dialog)),
                ft.TextButton(
                    "Reset All",
                    style=ft.ButtonStyle(color=ft.colors.ERROR),
                    on_click=lambda x: confirm_reset(confirm_dialog)
                )
            ]
        )
        
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()
    
    # Create save button
    save_button = ft.ElevatedButton(
        text="Save All Settings",
        icon=ft.icons.SAVE,
        on_click=on_save_click,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.PRIMARY,
            color=ft.colors.ON_PRIMARY,
            padding=16
        ),
        width=200,
        height=50
    )
    
    # Create reset button
    reset_button = ft.OutlinedButton(
        text="Reset to Defaults",
        icon=ft.icons.RESTORE,
        on_click=on_reset_click,
        style=ft.ButtonStyle(
            color=ft.colors.ERROR,
            padding=16
        ),
        width=200,
        height=50
    )
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Divider(height=2, thickness=2),
                ft.Row(
                    controls=[
                        save_button,
                        reset_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16,
                    wrap=True
                ),
                ft.Container(
                    content=ft.Text(
                        "💡 Most settings auto-save, but click 'Save All Settings' to ensure everything is saved.",
                        size=11,
                        color=ft.colors.OUTLINE,
                        text_align=ft.TextAlign.CENTER,
                        italic=True
                    ),
                    padding=ft.padding.only(top=8)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12
        ),
        padding=20,
        border=ft.border.all(2, ft.colors.PRIMARY),
        border_radius=12,
        bgcolor=ft.colors.SURFACE_VARIANT
    )


# THEN UPDATE THE build() METHOD:
# Replace the existing build() method with this:

def build(self):
    """Build the complete settings view"""
    
    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Text(
                    "Settings",
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),
                padding=16
            ),
            
            ft.ListView(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                self._create_theme_section(),     # Theme section
                                self._create_location_section(),   # Location
                                self._create_calculation_section(), # Calculation
                                self._create_jamaat_section(),     # Jamaat
                                self._create_app_section(),        # App settings
                                self._create_save_section(),       # NEW - Save/Reset buttons
                                ft.Container(height=20)
                            ],
                            spacing=16
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=8)
                    )
                ],
                expand=True,
                spacing=0,
                padding=0
            )
        ],
        expand=True,
        spacing=0
    )