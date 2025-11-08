"""
Diagnostic script to check all imports and dependencies
Run this before main.py to identify missing components
"""

import sys
from pathlib import Path

def check_module(module_path, class_name=None):
    """Check if a module and optional class can be imported"""
    try:
        module = __import__(module_path, fromlist=[class_name] if class_name else [])
        if class_name:
            if hasattr(module, class_name):
                print(f"✓ {module_path}.{class_name} - OK")
                return True
            else:
                print(f"✗ {module_path}.{class_name} - MISSING CLASS")
                return False
        else:
            print(f"✓ {module_path} - OK")
            return True
    except ImportError as e:
        print(f"✗ {module_path}{f'.{class_name}' if class_name else ''} - ERROR: {e}")
        return False
    except Exception as e:
        print(f"✗ {module_path}{f'.{class_name}' if class_name else ''} - UNEXPECTED ERROR: {e}")
        return False

def check_file_exists(file_path):
    """Check if a file exists"""
    path = Path(file_path)
    if path.exists():
        print(f"✓ {file_path} - EXISTS")
        return True
    else:
        print(f"✗ {file_path} - MISSING")
        return False

def main():
    print("=" * 60)
    print("PrayerOffline - Dependency Check")
    print("=" * 60)
    
    all_ok = True
    
    # Check external dependencies
    print("\n[1] External Dependencies:")
    print("-" * 60)
    external_deps = [
        ('flet', None),
        ('plyer', None),
        ('pytz', None),
        ('hijri_converter', None),
    ]
    
    for module, cls in external_deps:
        if not check_module(module, cls):
            all_ok = False
    
    # Check services
    print("\n[2] Service Modules:")
    print("-" * 60)
    services = [
        ('services.praytimes', 'PrayerTimesService'),
        ('services.notifier', 'NotificationService'),
        ('services.storage', 'StorageService'),
        ('services.location', 'LocationService'),
        ('services.audio_player', 'AudioPlayer'),
    ]
    
    for module, cls in services:
        if not check_module(module, cls):
            all_ok = False
    
    # Check views
    print("\n[3] View Modules:")
    print("-" * 60)
    views = [
        ('views.dashboard_view', 'DashboardView'),
        ('views.qibla_view', 'QiblaView'),
        ('views.settings_view', 'SettingsView'),
        ('views.dua_view', 'DuaView'),
        ('views.tasbih_view', 'TasbihView'),
    ]
    
    for module, cls in views:
        if not check_module(module, cls):
            all_ok = False
    
    # Check components
    print("\n[4] Component Modules:")
    print("-" * 60)
    components = [
        ('components.prayer_card', 'PrayerCard'),
        ('components.countdown_widget', 'CountdownWidget'),
        ('components.navigation_rail', 'AppNavigationRail'),
    ]
    
    for module, cls in components:
        if not check_module(module, cls):
            all_ok = False
    
    # Check utils
    print("\n[5] Utility Modules:")
    print("-" * 60)
    utils = [
        ('utils.constants', None),
        ('utils.helpers', None),
        ('utils.validators', None),
    ]
    
    for module, cls in utils:
        if not check_module(module, cls):
            all_ok = False
    
    # Check main files
    print("\n[6] Main Application Files:")
    print("-" * 60)
    main_files = [
        'main.py',
        'app.py',
    ]
    
    for file in main_files:
        if not check_file_exists(file):
            all_ok = False
    
    # Check directories
    print("\n[7] Required Directories:")
    print("-" * 60)
    directories = [
        'services',
        'views',
        'components',
        'utils',
        'assets',
        'assets/audio',
        'i18n',
    ]
    
    for dir_path in directories:
        if not check_file_exists(dir_path):
            all_ok = False
    
    # Check config files
    print("\n[8] Configuration Files:")
    print("-" * 60)
    config_files = [
        'requirements.txt',
        'i18n/strings.json',
    ]
    
    for file in config_files:
        check_file_exists(file)  # Not critical
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ ALL CHECKS PASSED - Ready to run!")
        print("\nRun the app with: python main.py")
    else:
        print("✗ SOME CHECKS FAILED - Please fix the issues above")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Ensure all service files have the required classes")
        print("  3. Check that __init__.py files exist in each package")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())