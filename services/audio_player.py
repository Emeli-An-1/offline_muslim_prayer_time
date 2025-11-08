"""
Audio Player Service for PrayerOffline App
Handles audio playback for Adhan and notifications
"""

import logging
from pathlib import Path
from typing import Optional

try:
    from plyer import audio
    AUDIO_AVAILABLE = True
except ImportError:
    audio = None
    AUDIO_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioPlayer:
    """Handles audio playback for Adhan and notifications"""
    
    def __init__(self, assets_path: Optional[str] = None):
        """
        Initialize audio player
        
        Args:
            assets_path: Path to audio assets directory
        """
        if assets_path is None:
            # Try to find assets directory relative to project root
            current_dir = Path(__file__).parent.parent
            assets_path = current_dir / "assets" / "audio"
        
        self.assets_path = Path(assets_path)
        self.is_playing = False
        self._current_file = None
        
        # Create assets directory if missing
        try:
            self.assets_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Audio assets path: {self.assets_path}")
        except Exception as e:
            logger.warning(f"Could not create audio assets directory: {e}")
        
        # Check for audio files
        self._check_audio_files()
    
    def _check_audio_files(self):
        """Check if audio files exist"""
        required_files = ["adhan.mp3", "notification.mp3"]
        
        for filename in required_files:
            file_path = self.assets_path / filename
            if file_path.exists():
                logger.info(f"Found audio file: {filename}")
            else:
                logger.warning(f"Audio file not found: {filename}")
    
    def play_adhan(self, audio_file: str = "adhan.mp3", blocking: bool = False) -> bool:
        """
        Play Adhan audio
        
        Args:
            audio_file: Adhan audio filename
            blocking: If True, wait for audio to finish
            
        Returns:
            True if playback started successfully
        """
        return self.play_file(audio_file, blocking=blocking)
    
    def play_notification_sound(self, audio_file: str = "notification.mp3", blocking: bool = False) -> bool:
        """
        Play notification sound
        
        Args:
            audio_file: Notification audio filename
            blocking: If True, wait for audio to finish
            
        Returns:
            True if playback started successfully
        """
        return self.play_file(audio_file, blocking=blocking)
    
    def play_file(self, filename: str, blocking: bool = False) -> bool:
        """
        Play an audio file
        
        Args:
            filename: Audio filename (with or without path)
            blocking: If True, wait for audio to finish
            
        Returns:
            True if playback started successfully
        """
        if not AUDIO_AVAILABLE:
            logger.warning("Audio playback not available (plyer not installed)")
            return False
        
        # Handle full path or just filename
        if Path(filename).is_absolute():
            audio_path = Path(filename)
        else:
            audio_path = self.assets_path / filename
        
        if not audio_path.exists():
            logger.warning(f"Audio file not found: {audio_path}")
            # Create a placeholder message
            logger.info("Audio playback would happen here if file existed")
            return False
        
        try:
            logger.info(f"Playing audio: {audio_path}")
            audio.play(str(audio_path))
            self.is_playing = True
            self._current_file = str(audio_path)
            
            if blocking:
                # Wait for audio to finish (simplified - actual implementation would need proper timing)
                import time
                time.sleep(1)  # Basic wait - would need actual duration detection
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop audio playback
        
        Returns:
            True if stopped successfully
        """
        if not AUDIO_AVAILABLE:
            return False
        
        try:
            if audio and self.is_playing:
                audio.stop()
                self.is_playing = False
                self._current_file = None
                logger.info("Audio playback stopped")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop audio: {e}")
            return False
    
    def is_audio_available(self) -> bool:
        """
        Check if audio playback is available
        
        Returns:
            True if audio is available
        """
        return AUDIO_AVAILABLE
    
    def get_available_audio_files(self) -> list:
        """
        Get list of available audio files
        
        Returns:
            List of audio filenames
        """
        try:
            audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
            files = []
            
            if self.assets_path.exists():
                for ext in audio_extensions:
                    files.extend([f.name for f in self.assets_path.glob(f'*{ext}')])
            
            return sorted(files)
            
        except Exception as e:
            logger.error(f"Error listing audio files: {e}")
            return []
    
    def get_current_file(self) -> Optional[str]:
        """
        Get currently playing file
        
        Returns:
            Path to current file or None
        """
        return self._current_file
    
    def set_volume(self, volume: float) -> bool:
        """
        Set playback volume (if supported)
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            True if volume set successfully
        """
        # Note: Plyer audio doesn't support volume control directly
        # This would need platform-specific implementation
        logger.warning("Volume control not implemented")
        return False
    
    def test_audio(self) -> bool:
        """
        Test audio playback
        
        Returns:
            True if test successful
        """
        logger.info("Testing audio playback...")
        
        if not AUDIO_AVAILABLE:
            logger.error("Audio not available - plyer not installed")
            return False
        
        # Try to play notification sound
        result = self.play_notification_sound()
        
        if result:
            logger.info("Audio test successful")
        else:
            logger.warning("Audio test failed - check audio files")
        
        return result
    
    def create_silent_audio_files(self):
        """
        Create placeholder audio files for testing
        (Creates very short silent MP3 files)
        """
        try:
            # This is a minimal silent MP3 file (44 bytes)
            silent_mp3 = bytes([
                0xFF, 0xFB, 0x90, 0x64, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00
            ])
            
            # Create placeholder files
            for filename in ["adhan.mp3", "notification.mp3"]:
                file_path = self.assets_path / filename
                if not file_path.exists():
                    with open(file_path, 'wb') as f:
                        f.write(silent_mp3)
                    logger.info(f"Created placeholder audio file: {filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create placeholder audio files: {e}")
            return False


def get_audio_player(assets_path: Optional[str] = None) -> AudioPlayer:
    """
    Get audio player instance
    
    Args:
        assets_path: Optional path to audio assets
        
    Returns:
        AudioPlayer instance
    """
    return AudioPlayer(assets_path=assets_path)


# Module-level audio player instance
_audio_player_instance = None


def get_singleton_audio_player() -> AudioPlayer:
    """
    Get singleton audio player instance
    
    Returns:
        Shared AudioPlayer instance
    """
    global _audio_player_instance
    
    if _audio_player_instance is None:
        _audio_player_instance = AudioPlayer()
    
    return _audio_player_instance