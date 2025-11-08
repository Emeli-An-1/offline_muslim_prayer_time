"""
Fix for settings_view.py - Manual Location Picker with Province Support
Run this script to automatically fix the _show_manual_location_picker method
"""

def get_fixed_method():
    return '''
def _show_manual_location_picker(self, e=None):
    """Show manual location picker dialog with province support"""
    locations_data = self._load_locations_data()
    countries = locations_data.get("countries", [])
    
    # State for dialog
    selected_country = None
    selected_province = None
    selected_city = None
    current_view = "countries"  # countries, provinces, cities
    
    # List view
    list_view = ft.ListView(
        height=350,
        spacing=4,
        padding=10
    )
    
    # Selected location display
    location_breadcrumb = ft.Text(
        "Select Country",
        size=14,
        color=ft.colors.OUTLINE
    )
    
    # Back button
    back_button = ft.IconButton(
        icon=ft.icons.ARROW_BACK,
        visible=False
    )
    
    # Dialog placeholder
    dlg = None
    
    def update_breadcrumb():
        if current_view == "countries":
            location_breadcrumb.value = "Select Country"
        elif current_view == "provinces":
            location_breadcrumb.value = f"{selected_country['name']} > Select Province"
        elif current_view == "cities":
            location_breadcrumb.value = f"{selected_country['name']} > {selected_province['name']} > Select City"
    
    def show_countries():
        nonlocal current_view
        current_view = "countries"
        list_view.controls.clear()
        
        for country in countries:
            item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.FLAG, size=20, color=ft.colors.PRIMARY),
                        ft.Text(country["name"], size=14, expand=True),
                        ft.Icon(ft.icons.ARROW_FORWARD_IOS, size=16, color=ft.colors.OUTLINE)
                    ]
                ),
                padding=12,
                border_radius=8,
                bgcolor=ft.colors.SURFACE,
                on_click=lambda e, c=country: on_country_select(c)
            )
            list_view.controls.append(item)
        
        update_breadcrumb()
        back_button.visible = False
        if dlg:
            dlg.update()
    
    def show_provinces(country):
        nonlocal current_view
        current_view = "provinces"
        list_view.controls.clear()
        
        provinces = country.get("provinces", [])
        
        for province in provinces:
            city_count = len(province.get("cities", []))
            item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.LOCATION_CITY, size=20, color=ft.colors.PRIMARY),
                        ft.Column(
                            controls=[
                                ft.Text(province["name"], size=14, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{city_count} cities", size=11, color=ft.colors.OUTLINE)
                            ],
                            spacing=2,
                            expand=True
                        ),
                        ft.Icon(ft.icons.ARROW_FORWARD_IOS, size=16, color=ft.colors.OUTLINE)
                    ]
                ),
                padding=12,
                border_radius=8,
                bgcolor=ft.colors.SURFACE,
                on_click=lambda e, p=province: on_province_select(p)
            )
            list_view.controls.append(item)
        
        update_breadcrumb()
        back_button.visible = True
        if dlg:
            dlg.update()
    
    def show_cities(province):
        nonlocal current_view
        current_view = "cities"
        list_view.controls.clear()
        
        cities = province.get("cities", [])
        
        for city in cities:
            item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.LOCATION_ON, size=20, color=ft.colors.PRIMARY),
                        ft.Text(city["name"], size=14, expand=True)
                    ]
                ),
                padding=12,
                border_radius=8,
                bgcolor=ft.colors.SURFACE,
                on_click=lambda e, c=city: on_city_select(c)
            )
            list_view.controls.append(item)
        
        update_breadcrumb()
        back_button.visible = True
        if dlg:
            dlg.update()
    
    def show_cities_for_country(country):
        """Show cities for countries without provinces"""
        nonlocal current_view
        current_view = "cities"
        list_view.controls.clear()
        
        cities = country.get("cities", [])
        
        for city in cities:
            item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.LOCATION_ON, size=20, color=ft.colors.PRIMARY),
                        ft.Text(city["name"], size=14, expand=True)
                    ]
                ),
                padding=12,
                border_radius=8,
                bgcolor=ft.colors.SURFACE,
                on_click=lambda e, c=city: on_city_select(c)
            )
            list_view.controls.append(item)
        
        update_breadcrumb()
        back_button.visible = True
        if dlg:
            dlg.update()
    
    def on_country_select(country):
        nonlocal selected_country
        selected_country = country
        
        # Check if country has provinces
        if country.get("has_provinces"):
            show_provinces(country)
        else:
            show_cities_for_country(country)
    
    def on_province_select(province):
        nonlocal selected_province
        selected_province = province
        show_cities(province)
    
    def on_city_select(city):
        nonlocal selected_city
        selected_city = city
        
        # Update settings and close
        self.settings["location"] = {
            "lat": city["lat"],
            "lng": city["lng"],
            "latitude": city["lat"],
            "longitude": city["lng"],
            "city": city["name"],
            "country": selected_country["name"],
            "timezone": city.get("timezone", "UTC")
        }
        self._save_settings()
        self._update_location_display()
        
        if dlg:
            dlg.open = False
        self.page.update()
        self._show_snackbar(f"Location set to {city['name']}, {selected_country['name']}")
    
    def on_back_click(e):
        if current_view == "cities":
            if selected_country and selected_country.get("has_provinces"):
                show_provinces(selected_country)
            else:
                show_countries()
        elif current_view == "provinces":
            show_countries()
    
    def on_close(e):
        if dlg:
            dlg.open = False
            self.page.update()
    
    # Set back button handler
    back_button.on_click = on_back_click
    
    # Create dialog
    dlg = ft.AlertDialog(
        title=ft.Row(
            controls=[
                back_button,
                ft.Text("Select Location", size=20, expand=True)
            ]
        ),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    location_breadcrumb,
                    ft.Divider(height=1),
                    list_view
                ],
                spacing=12,
                tight=True
            ),
            width=450,
            height=450
        ),
        actions=[
            ft.TextButton("Cancel", on_click=on_close)
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    
    # Initialize with countries
    show_countries()
    
    # Show dialog
    self.page.dialog = dlg
    dlg.open = True
    self.page.update()
'''

def apply_fix():
    """Apply the fix to settings_view.py"""
    import re
    from pathlib import Path
    
    settings_file = Path("views/settings_view.py")
    
    if not settings_file.exists():
        print("Error: views/settings_view.py not found")
        return False
    
    # Read current content
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the _show_manual_location_picker method
    pattern = r'(    def _show_manual_location_picker\(self.*?)(    def \w+\(self|class \w+:|$)'
    
    fixed_method = get_fixed_method()
    
    # Check if method exists
    if 'def _show_manual_location_picker' in content:
        # Replace existing method
        new_content = re.sub(
            pattern,
            r'\1' + fixed_method + '\n\n' + r'\2',
            content,
            flags=re.DOTALL
        )
        
        # Backup original
        backup_file = settings_file.with_suffix('.py.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Backup created: {backup_file}")
        
        # Write fixed version
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✓ Fixed _show_manual_location_picker method")
        return True
    else:
        print("Warning: _show_manual_location_picker method not found")
        print("Add this method manually to SettingsView class:")
        print(fixed_method)
        return False

if __name__ == "__main__":
    print("Applying fix to settings_view.py...")
    if apply_fix():
        print("\n✓ Fix applied successfully!")
        print("Run your app: py main.py")
    else:
        print("\n✗ Fix failed. Apply manually.")