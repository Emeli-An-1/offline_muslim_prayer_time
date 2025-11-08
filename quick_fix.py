"""
Quick Fix Script - Automatically adds missing class stubs
Run this to fix import errors quickly
"""

import os
from pathlib import Path

def ensure_directory(path):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"✓ Ensured directory: {path}")

def create_init_file(directory):
    """Create __init__.py if missing"""
    init_file = Path(directory) / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")
        print(f"✓ Created: {init_file}")

def fix_audio_player():
    """Fix audio_player.py to include AudioPlayer class"""
    content = '''"""
Audio Player Service for PrayerOffline App
"""

import logging
from pathlib import Path

try:
    from plyer import audio
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

logger = logging.getLogger(__name__)

class AudioPlayer:
    """Handles audio playback for Adhan and notifications"""
    
    def __init__(self, assets_path: str = "assets/audio"):
        self.assets_path = Path(assets_path)
        self.is_playing = False
        
        # Create assets directory if missing
        self.assets_path.mkdir(parents=True, exist_ok=True)
    
    def play_adhan(self, audio_file: str = "adhan.mp3") -> bool:
        """Play Adhan audio"""
        return self._play_audio(audio_file)
    
    def play_notification(self, audio_file: str = "notification.mp3") -> bool:
        """Play notification sound"""
        return self._play_audio(audio_file)
    
    def _play_audio(self, filename: str) -> bool:
        """Internal audio playback"""
        if not PLYER_AVAILABLE:
            logger.warning("Audio playback not available")
            return False
        
        audio_path = self.assets_path / filename
        if not audio_path.exists():
            logger.warning(f"Audio file not found: {audio_path}")
            return False
        
        try:
            audio.play(str(audio_path))
            self.is_playing = True
            return True
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop audio playback"""
        if PLYER_AVAILABLE:
            try:
                audio.stop()
                self.is_playing = False
                return True
            except Exception:
                pass
        return False
    
    def is_audio_available(self) -> bool:
        """Check if audio is available"""
        return PLYER_AVAILABLE

def get_audio_player():
    """Get audio player instance"""
    return AudioPlayer()
'''
    
    file_path = Path("services/audio_player.py")
    file_path.write_text(content)
    print(f"✓ Fixed: {file_path}")

def check_and_fix_service(service_name, class_name):
    """Check if service has the required class, add stub if missing"""
    file_path = Path(f"services/{service_name}.py")
    
    if not file_path.exists():
        print(f"✗ Missing: {file_path}")
        return False
    
    content = file_path.read_text()
    
    if f"class {class_name}" not in content:
        print(f"⚠ Class {class_name} not found in {file_path}")
        # Add class stub at the end
        stub = f'''

class {class_name}:
    """Placeholder for {class_name} - needs implementation"""
    def __init__(self):
        pass
'''
        file_path.write_text(content + stub)
        print(f"✓ Added stub class {class_name} to {file_path}")
        return True
    
    return True

def main():
    print("=" * 60)
    print("PrayerOffline - Quick Fix Tool")
    print("=" * 60)
    
    # Ensure directories exist
    print("\n[1] Ensuring directories exist...")
    directories = ['services', 'views', 'components', 'utils', 'assets', 'assets/audio', 'i18n']
    for directory in directories:
        ensure_directory(directory)
        create_init_file(directory)
    
    # Fix audio_player specifically
    print("\n[2] Fixing audio_player.py...")
    fix_audio_player()
    
    # Check other services
    print("\n[3] Checking other services...")
    services = [
        ('praytimes', 'PrayerTimesService'),
        ('notifier', 'NotificationService'),
        ('storage', 'StorageService'),
        ('location', 'LocationService'),
    ]
    
    for service_file, class_name in services:
        check_and_fix_service(service_file, class_name)
    
    print("\n" + "=" * 60)
    print("✓ Quick fix completed!")
    print("\nNext steps:")
    print("  1. Run: python check_imports.py")
    print("  2. If all checks pass, run: python main.py")
    print("=" * 60)

if __name__ == "__main__":
    main()