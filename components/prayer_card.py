"""
Prayer Card Component for displaying individual prayer times
Reusable card component with Adhan and Jamaat times
"""

import flet as ft
from typing import Dict, Any, Callable, Optional


class PrayerCard:
    """Component class for displaying prayer time information"""
    
    def __init__(
        self,
        page: ft.Page,
        prayer_name: str,
        prayer_data: Dict[str, Any],
        show_jamaat: bool = True,
        is_active: bool = False,
        on_edit_jamaat: Optional[Callable] = None
    ):
        """
        Initialize prayer card component
        
        Args:
            page: Flet page instance for updates
            prayer_name: Name of the prayer (Fajr, Dhuhr, etc.)
            prayer_data: Dictionary with 'adhan' and 'jamaat' times
            show_jamaat: Whether to show jamaat time row
            is_active: Highlight as next/current prayer
            on_edit_jamaat: Optional callback for editing jamaat time
        """
        self.page = page
        self.prayer_name = prayer_name
        self.prayer_data = prayer_data
        self.show_jamaat = show_jamaat
        self.is_active = is_active
        self.on_edit_jamaat = on_edit_jamaat
        
        # UI Components references
        self.container = None
        self.header_icon = None
        self.header_text = None
        self.adhan_time_text = None
        self.jamaat_row = None
        self.jamaat_time_text = None
        
    def build(self) -> ft.Control:
        """Build and return the prayer card as a Container"""
        try:
            # Extract prayer times
            adhan_time = self.prayer_data.get("adhan", "N/A")
            jamaat_time = self.prayer_data.get("jamaat", "")
            
            # Prayer icon
            prayer_icon = self._get_prayer_icon(self.prayer_name)
            
            # Header components with references
            self.header_icon = ft.Icon(
                prayer_icon,
                size=24,
                color=ft.Colors.PRIMARY if self.is_active else ft.Colors.ON_SURFACE
            )
            
            self.header_text = ft.Text(
                self.prayer_name,
                size=18,
                weight=ft.FontWeight.BOLD if self.is_active else ft.FontWeight.W_500,
                color=ft.Colors.PRIMARY if self.is_active else ft.Colors.ON_SURFACE
            )
            
            header = ft.Row(
                controls=[self.header_icon, self.header_text],
                spacing=8,
                alignment=ft.MainAxisAlignment.START
            )
            
            # Adhan time row with reference
            self.adhan_time_text = ft.Text(
                adhan_time,
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.ON_SURFACE
            )
            
            adhan_row = ft.Row(
                controls=[
                    ft.Text("Adhan:", size=14, color=ft.Colors.OUTLINE),
                    self.adhan_time_text,
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            
            # Jamaat time row with reference
            self.jamaat_time_text = ft.Text(
                jamaat_time if jamaat_time else "Not set",
                size=16,
                weight=ft.FontWeight.BOLD if jamaat_time else ft.FontWeight.NORMAL,
                color=ft.Colors.ON_SURFACE if jamaat_time else ft.Colors.OUTLINE
            )
            
            jamaat_controls = [
                ft.Text("Jamaat:", size=14, color=ft.Colors.OUTLINE),
                self.jamaat_time_text,
            ]
            
            # Add edit button if callback provided
            if self.on_edit_jamaat and jamaat_time:
                jamaat_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_size=16,
                        tooltip="Edit jamaat time",
                        on_click=lambda _: self.on_edit_jamaat()
                    )
                )
            
            self.jamaat_row = ft.Row(
                controls=jamaat_controls,
                spacing=8,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                visible=self.show_jamaat
            )
            
            # Main content column
            content = ft.Column(
                controls=[
                    header,
                    ft.Divider(height=1, thickness=1),
                    adhan_row,
                    self.jamaat_row,
                ],
                spacing=8,
            )
            
            # Card container with reference
            self.container = ft.Container(
                content=content,
                bgcolor=ft.Colors.PRIMARY_CONTAINER if self.is_active else ft.Colors.SURFACE_VARIANT,
                border=ft.border.all(
                    2,
                    ft.Colors.PRIMARY if self.is_active else ft.Colors.OUTLINE_VARIANT
                ),
                border_radius=12,
                padding=16,
            )
            
            return self.container
            
        except Exception as e:
            # Fallback error card
            return ft.Container(
                content=ft.Text(
                    f"Error loading {self.prayer_name}",
                    color=ft.Colors.ERROR
                ),
                bgcolor=ft.Colors.ERROR_CONTAINER,
                border_radius=12,
                padding=16,
            )
    
    def _get_prayer_icon(self, prayer_name: str) -> str:
        """Get appropriate icon for prayer"""
        icons = {
            "Fajr": ft.Icons.WB_TWILIGHT,
            "Sunrise": ft.Icons.WB_SUNNY,
            "Dhuhr": ft.Icons.LIGHT_MODE,
            "Asr": ft.Icons.BRIGHTNESS_6,
            "Maghrib": ft.Icons.BRIGHTNESS_4,
            "Isha": ft.Icons.BRIGHTNESS_2,
        }
        return icons.get(prayer_name, ft.Icons.ACCESS_TIME)
    
    def update_jamaat_visibility(self, show_jamaat: bool):
        """
        Update jamaat time visibility
        
        Args:
            show_jamaat: Whether to show jamaat row
        """
        self.show_jamaat = show_jamaat
        if self.jamaat_row:
            self.jamaat_row.visible = show_jamaat
            if self.page:
                self.page.update()
    
    def update_active_state(self, is_active: bool):
        """
        Update card active/highlighted state
        
        Args:
            is_active: Whether this is the active (next) prayer
        """
        self.is_active = is_active
        
        # Update container styling
        if self.container:
            self.container.bgcolor = (
                ft.Colors.PRIMARY_CONTAINER if is_active 
                else ft.Colors.SURFACE_VARIANT
            )
            self.container.border = ft.border.all(
                2,
                ft.Colors.PRIMARY if is_active else ft.Colors.OUTLINE_VARIANT
            )
        
        # Update header styling
        if self.header_icon:
            self.header_icon.color = (
                ft.Colors.PRIMARY if is_active 
                else ft.Colors.ON_SURFACE
            )
        
        if self.header_text:
            self.header_text.weight = (
                ft.FontWeight.BOLD if is_active 
                else ft.FontWeight.W_500
            )
            self.header_text.color = (
                ft.Colors.PRIMARY if is_active 
                else ft.Colors.ON_SURFACE
            )
        
        if self.page:
            self.page.update()
    
    def update_times(self, adhan_time: str, jamaat_time: str = ""):
        """
        Update prayer times
        
        Args:
            adhan_time: New adhan time
            jamaat_time: New jamaat time (optional)
        """
        self.prayer_data["adhan"] = adhan_time
        self.prayer_data["jamaat"] = jamaat_time
        
        # Update text components
        if self.adhan_time_text:
            self.adhan_time_text.value = adhan_time
        
        if self.jamaat_time_text:
            self.jamaat_time_text.value = jamaat_time if jamaat_time else "Not set"
            self.jamaat_time_text.weight = (
                ft.FontWeight.BOLD if jamaat_time 
                else ft.FontWeight.NORMAL
            )
            self.jamaat_time_text.color = (
                ft.Colors.ON_SURFACE if jamaat_time 
                else ft.Colors.OUTLINE
            )
        
        if self.page:
            self.page.update()


# Factory function for easy card creation
def create_prayer_card(
    page: ft.Page,
    prayer_name: str,
    adhan_time: str,
    jamaat_time: str = "",
    show_jamaat: bool = True,
    is_active: bool = False,
    on_edit_jamaat: Optional[Callable] = None
) -> ft.Control:
    """
    Factory function to create a prayer card
    
    Args:
        page: Flet page instance
        prayer_name: Prayer name
        adhan_time: Adhan time (HH:MM format)
        jamaat_time: Jamaat time (HH:MM format, optional)
        show_jamaat: Show jamaat row
        is_active: Highlight as active
        on_edit_jamaat: Edit callback
        
    Returns:
        Built Flet control (Container)
        
    Example:
        card = create_prayer_card(
            page=page,
            prayer_name="Fajr",
            adhan_time="05:30",
            jamaat_time="05:45",
            is_active=True
        )
    """
    prayer_data = {
        "adhan": adhan_time,
        "jamaat": jamaat_time
    }
    
    card = PrayerCard(
        page=page,
        prayer_name=prayer_name,
        prayer_data=prayer_data,
        show_jamaat=show_jamaat,
        is_active=is_active,
        on_edit_jamaat=on_edit_jamaat
    )
    
    return card.build()