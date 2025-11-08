"""
Flet Prayer App - Complete Language & Localization System
Integrates with your prayer_offline project
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class LanguageCode(Enum):
    """Supported language codes."""
    ARABIC = "ar"
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    INDONESIAN = "id"
    MALAY = "ms"
    TURKISH = "tr"
    URDU = "ur"
    PERSIAN = "fa"
    RUSSIAN = "ru"
    SPANISH = "es"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    BENGALI = "bn"
    HINDI = "hi"


@dataclass
class LanguageInfo:
    """Language metadata."""
    code: str
    name: str
    native_name: str
    is_rtl: bool
    flag_emoji: str


class LanguageManager:
    """Manages language settings and translations."""
    
    LANGUAGES: Dict[str, LanguageInfo] = {
        "ar": LanguageInfo("ar", "Arabic", "العربية", True, "🇸🇦"),
        "en": LanguageInfo("en", "English", "English", False, "🇬🇧"),
        "fr": LanguageInfo("fr", "French", "Français", False, "🇫🇷"),
        "de": LanguageInfo("de", "German", "Deutsch", False, "🇩🇪"),
        "id": LanguageInfo("id", "Indonesian", "Bahasa Indonesia", False, "🇮🇩"),
        "ms": LanguageInfo("ms", "Malay", "Bahasa Melayu", False, "🇲🇾"),
        "tr": LanguageInfo("tr", "Turkish", "Türkçe", False, "🇹🇷"),
        "ur": LanguageInfo("ur", "Urdu", "اردو", True, "🇵🇰"),
        "fa": LanguageInfo("fa", "Persian", "فارسی", True, "🇮🇷"),
        "ru": LanguageInfo("ru", "Russian", "Русский", False, "🇷🇺"),
        "es": LanguageInfo("es", "Spanish", "Español", False, "🇪🇸"),
        "pt": LanguageInfo("pt", "Portuguese", "Português", False, "🇵🇹"),
        "zh": LanguageInfo("zh", "Chinese", "中文", False, "🇨🇳"),
        "bn": LanguageInfo("bn", "Bengali", "বাংলা", False, "🇧🇩"),
        "hi": LanguageInfo("hi", "Hindi", "हिन्दी", False, "🇮🇳"),
    }
    
    # Prayer time translations
    PRAYERS: Dict[str, Dict[str, str]] = {
        "fajr": {
            "ar": "الفجر", "en": "Fajr", "fr": "Fajr", "de": "Fadschr",
            "id": "Subuh", "ms": "Subuh", "tr": "İmsak", "ur": "فجر",
            "fa": "صبح", "ru": "Фаджр", "es": "Fajr", "pt": "Fajr",
            "zh": "晨礼", "bn": "ফজর", "hi": "फ़ज्र"
        },
        "dhuhr": {
            "ar": "الظهر", "en": "Dhuhr", "fr": "Dhuhr", "de": "Zuhr",
            "id": "Dzuhur", "ms": "Zohor", "tr": "Öğle", "ur": "ظہر",
            "fa": "ظهر", "ru": "Зухр", "es": "Dhuhr", "pt": "Dhuhr",
            "zh": "晌礼", "bn": "যোহর", "hi": "ज़ुहर"
        },
        "asr": {
            "ar": "العصر", "en": "Asr", "fr": "Asr", "de": "Asr",
            "id": "Ashar", "ms": "Asar", "tr": "İkindi", "ur": "عصر",
            "fa": "عصر", "ru": "Аср", "es": "Asr", "pt": "Asr",
            "zh": "晡礼", "bn": "আসর", "hi": "अस्र"
        },
        "maghrib": {
            "ar": "المغرب", "en": "Maghrib", "fr": "Maghrib", "de": "Maghrib",
            "id": "Maghrib", "ms": "Maghrib", "tr": "Akşam", "ur": "مغرب",
            "fa": "مغرب", "ru": "Магриб", "es": "Maghrib", "pt": "Maghrib",
            "zh": "昏礼", "bn": "মাগরিব", "hi": "मग़रिब"
        },
        "isha": {
            "ar": "العشاء", "en": "Isha", "fr": "Isha", "de": "Ischa",
            "id": "Isya", "ms": "Isyak", "tr": "Yatsı", "ur": "عشاء",
            "fa": "عشاء", "ru": "Иша", "es": "Isha", "pt": "Isha",
            "zh": "宵礼", "bn": "ইশা", "hi": "इशा"
        }
    }
    
    # UI translations
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        "app_title": {
            "ar": "أوقات الصلاة", "en": "Prayer Times", "fr": "Heures de Prière",
            "de": "Gebetszeiten", "id": "Waktu Sholat", "ms": "Waktu Solat",
            "tr": "Namaz Vakitleri", "ur": "نماز کے اوقات", "fa": "اوقات نماز",
            "ru": "Времена молитв", "es": "Horarios de Oración", "pt": "Horários de Oração",
            "zh": "礼拜时间", "bn": "নামাজের সময়", "hi": "नमाज़ का समय"
        },
        "next_prayer": {
            "ar": "الصلاة القادمة", "en": "Next Prayer", "fr": "Prochaine Prière",
            "de": "Nächstes Gebet", "id": "Sholat Berikutnya", "ms": "Solat Seterusnya",
            "tr": "Sonraki Namaz", "ur": "اگلی نماز", "fa": "نماز بعدی",
            "ru": "Следующая молитва", "es": "Próxima Oración", "pt": "Próxima Oração",
            "zh": "下次礼拜", "bn": "পরবর্তী নামাজ", "hi": "अगली नमाज़"
        },
        "time_remaining": {
            "ar": "الوقت المتبقي", "en": "Time Remaining", "fr": "Temps Restant",
            "de": "Verbleibende Zeit", "id": "Waktu Tersisa", "ms": "Masa Berbaki",
            "tr": "Kalan Süre", "ur": "باقی وقت", "fa": "زمان باقی‌مانده",
            "ru": "Осталось времени", "es": "Tiempo Restante", "pt": "Tempo Restante",
            "zh": "剩余时间", "bn": "অবশিষ্ট সময়", "hi": "शेष समय"
        },
        "location": {
            "ar": "الموقع", "en": "Location", "fr": "Emplacement",
            "de": "Standort", "id": "Lokasi", "ms": "Lokasi",
            "tr": "Konum", "ur": "مقام", "fa": "موقعیت",
            "ru": "Местоположение", "es": "Ubicación", "pt": "Localização",
            "zh": "位置", "bn": "অবস্থান", "hi": "स्थान"
        },
        "settings": {
            "ar": "الإعدادات", "en": "Settings", "fr": "Paramètres",
            "de": "Einstellungen", "id": "Pengaturan", "ms": "Tetapan",
            "tr": "Ayarlar", "ur": "ترتیبات", "fa": "تنظیمات",
            "ru": "Настройки", "es": "Configuración", "pt": "Configurações",
            "zh": "设置", "bn": "সেটিংস", "hi": "सेटिंग्स"
        },
        "language": {
            "ar": "اللغة", "en": "Language", "fr": "Langue",
            "de": "Sprache", "id": "Bahasa", "ms": "Bahasa",
            "tr": "Dil", "ur": "زبان", "fa": "زبان",
            "ru": "Язык", "es": "Idioma", "pt": "Idioma",
            "zh": "语言", "bn": "ভাষা", "hi": "भाषा"
        },
        "calculation_method": {
            "ar": "طريقة الحساب", "en": "Calculation Method", "fr": "Méthode de Calcul",
            "de": "Berechnungsmethode", "id": "Metode Perhitungan", "ms": "Kaedah Pengiraan",
            "tr": "Hesaplama Yöntemi", "ur": "حساب کا طریقہ", "fa": "روش محاسبه",
            "ru": "Метод расчета", "es": "Método de Cálculo", "pt": "Método de Cálculo",
            "zh": "计算方法", "bn": "গণনা পদ্ধতি", "hi": "गणना विधि"
        },
        "notifications": {
            "ar": "الإشعارات", "en": "Notifications", "fr": "Notifications",
            "de": "Benachrichtigungen", "id": "Notifikasi", "ms": "Pemberitahuan",
            "tr": "Bildirimler", "ur": "اطلاعات", "fa": "اعلان‌ها",
            "ru": "Уведомления", "es": "Notificaciones", "pt": "Notificações",
            "zh": "通知", "bn": "বিজ্ঞপ্তি", "hi": "सूचनाएं"
        },
        "qibla_direction": {
            "ar": "اتجاه القبلة", "en": "Qibla Direction", "fr": "Direction Qibla",
            "de": "Qibla-Richtung", "id": "Arah Kiblat", "ms": "Arah Kiblat",
            "tr": "Kıble Yönü", "ur": "قبلہ کی سمت", "fa": "جهت قبله",
            "ru": "Направление Киблы", "es": "Dirección Qibla", "pt": "Direção Qibla",
            "zh": "朝拜方向", "bn": "কিবলা দিক", "hi": "क़िबला दिशा"
        }
    }
    
    def __init__(self, default_lang: str = "en", config_path: Optional[Path] = None):
        """Initialize language manager."""
        self.current_language = default_lang
        self.config_path = config_path or Path("config/language.json")
        self._load_saved_language()
    
    def _load_saved_language(self):
        """Load saved language preference."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_language = config.get('language', self.current_language)
        except Exception as e:
            print(f"Could not load language config: {e}")
    
    def save_language(self, lang_code: str) -> bool:
        """Save language preference."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({'language': lang_code}, f, ensure_ascii=False, indent=2)
            self.current_language = lang_code
            return True
        except Exception as e:
            print(f"Could not save language config: {e}")
            return False
    
    def get_language_info(self, lang_code: Optional[str] = None) -> LanguageInfo:
        """Get language information."""
        code = lang_code or self.current_language
        return self.LANGUAGES.get(code, self.LANGUAGES["en"])
    
    def is_rtl(self, lang_code: Optional[str] = None) -> bool:
        """Check if language is RTL."""
        return self.get_language_info(lang_code).is_rtl
    
    def translate(self, key: str, lang_code: Optional[str] = None) -> str:
        """Get translation for a key."""
        code = lang_code or self.current_language
        
        # Check UI translations
        if key in self.TRANSLATIONS:
            return self.TRANSLATIONS[key].get(code, self.TRANSLATIONS[key]["en"])
        
        # Check prayer names
        if key in self.PRAYERS:
            return self.PRAYERS[key].get(code, self.PRAYERS[key]["en"])
        
        return key
    
    def get_prayer_name(self, prayer: str, lang_code: Optional[str] = None) -> str:
        """Get localized prayer name."""
        return self.translate(prayer.lower(), lang_code)
    
    def get_all_languages(self) -> Dict[str, LanguageInfo]:
        """Get all available languages."""
        return self.LANGUAGES
    
    def set_language(self, lang_code: str) -> bool:
        """Set current language."""
        if lang_code in self.LANGUAGES:
            self.current_language = lang_code
            return self.save_language(lang_code)
        return False


# Singleton instance
_language_manager: Optional[LanguageManager] = None

def get_language_manager() -> LanguageManager:
    """Get global language manager instance."""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager


# Convenience function
def t(key: str) -> str:
    """Quick translation function."""
    return get_language_manager().translate(key)


# Example usage
if __name__ == "__main__":
    # Initialize
    lm = LanguageManager(default_lang="en")
    
    # Get translations
    print(f"App Title (EN): {lm.translate('app_title', 'en')}")
    print(f"App Title (AR): {lm.translate('app_title', 'ar')}")
    print(f"App Title (TR): {lm.translate('app_title', 'tr')}")
    
    # Get prayer names
    print(f"\nFajr (EN): {lm.get_prayer_name('fajr', 'en')}")
    print(f"Fajr (AR): {lm.get_prayer_name('fajr', 'ar')}")
    print(f"Fajr (ID): {lm.get_prayer_name('fajr', 'id')}")
    
    # Check RTL
    print(f"\nArabic RTL: {lm.is_rtl('ar')}")
    print(f"English RTL: {lm.is_rtl('en')}")
    
    # List all languages
    print("\nAvailable Languages:")
    for code, info in lm.get_all_languages().items():
        print(f"  {info.flag_emoji} {info.native_name} ({info.name}) - RTL: {info.is_rtl}")