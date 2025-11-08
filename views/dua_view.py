"""
Enhanced Dua View - WITH THEME SUPPORT
Added theme_manager parameter and themed styling
"""

import flet as ft
from typing import List, Dict, Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DuaView:
    """Comprehensive Dua view with theme support"""

    DUAS_DATABASE = {
        "morning": [
            {
                "id": "morning_001",
                "arabic": "بِسْمِ اللَّهِ الَّذِي لَا يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الْأَرْضِ وَلَا فِي السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ",
                "transliteration": "Bismillahil-lazi la yadhuru ma'a ismihi shay'un fil-ardi wa la fis-sama'i wa Huwa As-Samee'ul-'Aleem",
                "translation": "In the name of Allah, with whose name nothing on earth or in the heavens can cause harm, and He is the All-Hearing, All-Knowing",
                "category": "morning"
            },
            {
                "id": "morning_002",
                "arabic": "اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ",
                "transliteration": "Allahumma bika asbahna wa bika amsayna wa bika nahya wa bika namutu wa ilaykal-nushur",
                "translation": "O Allah, by You we enter the morning and by You we enter the evening, by You we live and by You we die, and to You is the resurrection",
                "category": "morning"
            }
        ],
        "evening": [
            {
                "id": "evening_001",
                "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَافِيَةَ فِي الدُّنْيَا وَالْآخِرَةِ",
                "transliteration": "Allahumma inni as'aluka al-'afiyata fil-dunya wal-akhirah",
                "translation": "O Allah, I ask You for well-being in this life and the next",
                "category": "evening"
            }
        ],
        "before_prayer": [
            {
                "id": "before_prayer_001",
                "arabic": "رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ",
                "transliteration": "Rabbi ighfir li wa tub alayya innaka anta at-Tawwabu ar-Rahim",
                "translation": "My Lord, forgive me and turn to me, indeed You are the Ever-Returning, the Merciful",
                "category": "before_prayer"
            }
        ],
        "after_prayer": [
            {
                "id": "after_prayer_001",
                "arabic": "اللَّهُمَّ أَنْتَ السَّلَامُ وَمِنْكَ السَّلَامُ تَبَارَكْتَ يَا ذَا الْجَلَالِ وَالْإِكْرَامِ",
                "transliteration": "Allahumma anta as-Salam wa minka as-Salam tabarakta ya dhal-Jalali wal-Ikram",
                "translation": "O Allah, You are As-Salam (the Source of Peace), and from You is all peace, blessed are You, O Possessor of Majesty and Honor",
                "category": "after_prayer"
            }
        ],
        "general": [
            {
                "id": "general_001",
                "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ",
                "transliteration": "Rabbana atina fid-dunya hasanatan wa fil-akhirati hasanatan wa qina 'adhaban-nar",
                "translation": "Our Lord, give us good in this world and good in the hereafter, and save us from the punishment of the Fire",
                "category": "general"
            }
        ]
    }

    CATEGORIES = {
        "morning": {"label": "Morning", "icon": ft.Icons.LIGHT_MODE},
        "evening": {"label": "Evening", "icon": ft.Icons.DARK_MODE},
        "before_prayer": {"label": "Before Prayer", "icon": ft.Icons.ACCESS_TIME},
        "after_prayer": {"label": "After Prayer", "icon": ft.Icons.CHECK_CIRCLE},
        "general": {"label": "General", "icon": ft.Icons.FAVORITE}
    }

    def __init__(
        self,
        page: ft.Page,
        storage_service,
        audio_service=None,
        theme_manager=None,  # NEW - Added theme_manager
        i18n_strings: Dict = None
    ):
        """Initialize Dua View with theme support"""
        self.page = page
        self.storage = storage_service
        self.audio = audio_service
        self.theme_manager = theme_manager  # NEW - Store theme_manager
        self.strings = i18n_strings or {}
        self.bookmarks = set()
        self.current_category = "morning"
        self.search_query = ""
        self.current_language = "en"
        
        self._load_bookmarks()
        self.build()

    def _load_bookmarks(self):
        try:
            bookmarks = self.storage.get("dua_bookmarks", [])
            self.bookmarks = set(bookmarks)
            logger.info(f"Loaded {len(self.bookmarks)} bookmarks")
        except Exception as e:
            logger.error(f"Failed to load bookmarks: {e}")
            self.bookmarks = set()

    def _save_bookmarks(self):
        try:
            self.storage.set("dua_bookmarks", list(self.bookmarks))
        except Exception as e:
            logger.error(f"Failed to save bookmarks: {e}")

    def _get_filtered_duas(self) -> List[Dict]:
        duas = self.DUAS_DATABASE.get(self.current_category, [])
        if not self.search_query:
            return duas
        query = self.search_query.lower()
        filtered = []
        for dua in duas:
            if (query in dua.get("arabic", "").lower() or
                query in dua.get("transliteration", "").lower() or
                query in dua.get("translation", "").lower()):
                filtered.append(dua)
        return filtered

    def _on_search_change(self, e: ft.ControlEvent):
        self.search_query = e.control.value
        self._update_duas_display()

    def _on_category_change(self, category: str):
        self.current_category = category
        self.search_query = ""
        self.search_field.value = ""
        self._update_duas_display()

    def _toggle_bookmark(self, dua_id: str):
        if dua_id in self.bookmarks:
            self.bookmarks.discard(dua_id)
        else:
            self.bookmarks.add(dua_id)
        self._save_bookmarks()
        self._update_duas_display()

    def _update_duas_display(self):
        duas = self._get_filtered_duas()
        self.duas_container.controls.clear()
        
        if not duas:
            self.duas_container.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No duas found",
                        size=16,
                        color=ft.colors.OUTLINE_VARIANT
                    ),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for dua in duas:
                self.duas_container.controls.append(
                    self._create_dua_card(dua)
                )
        self.page.update()

    def _create_dua_card(self, dua: Dict) -> ft.Container:
        """Create a dua display card with theme"""
        is_bookmarked = dua["id"] in self.bookmarks
        
        # NEW - Get theme colors
        if self.theme_manager:
            theme = self.theme_manager.get_theme()
            primary_color = theme.colors.primary
            surface_color = theme.colors.surface
            on_surface_color = theme.colors.on_surface
            outline_color = theme.colors.divider
        else:
            primary_color = ft.colors.PRIMARY
            surface_color = ft.colors.SURFACE
            on_surface_color = ft.colors.ON_SURFACE
            outline_color = ft.colors.OUTLINE
        
        bookmark_btn = ft.IconButton(
            icon=ft.Icons.BOOKMARK if is_bookmarked else ft.Icons.BOOKMARK_BORDER,
            icon_color=primary_color if is_bookmarked else outline_color,  # NEW - Themed
            on_click=lambda _: self._toggle_bookmark(dua["id"])
        )
        
        share_btn = ft.IconButton(
            icon=ft.Icons.SHARE,
            icon_color=outline_color,  # NEW - Themed
            on_click=lambda _: self._share_dua(dua)
        )
        
        play_btn = ft.IconButton(
            icon=ft.Icons.PLAY_CIRCLE,
            icon_color=primary_color,  # NEW - Themed
            on_click=lambda _: self._play_dua_audio(dua["id"]),
            visible=self.audio is not None
        )
        
        # NEW - Use theme card style if available
        card_style = {}
        if self.theme_manager:
            card_style = self.theme_manager.get_card_style()
        else:
            card_style = {
                "padding": 12,
                "margin": ft.margin.symmetric(vertical=8, horizontal=0),
                "border": ft.border.all(1, ft.colors.OUTLINE),
                "border_radius": 12
            }
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            dua["arabic"],
                            size=20,
                            weight=ft.FontWeight.W_600,
                            text_align=ft.TextAlign.RIGHT,
                            color=on_surface_color  # NEW - Themed
                        ),
                        padding=16,
                        bgcolor=surface_color,  # NEW - Themed
                        border_radius=8
                    ),
                    ft.Container(
                        content=ft.Text(
                            dua["transliteration"],
                            size=12,
                            italic=True,
                            color=ft.colors.OUTLINE,
                            selectable=True
                        ),
                        padding=12
                    ),
                    ft.Container(
                        content=ft.Text(
                            dua["translation"],
                            size=14,
                            color=ft.colors.ON_SURFACE_VARIANT,
                            selectable=True
                        ),
                        padding=12
                    ),
                    ft.Row(
                        controls=[play_btn, share_btn, bookmark_btn],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                spacing=0
            ),
            **card_style  # NEW - Apply theme card style
        )

    def _share_dua(self, dua: Dict):
        try:
            share_text = (
                f"{dua['arabic']}\n\n"
                f"{dua['transliteration']}\n\n"
                f"{dua['translation']}\n\n"
                f"Shared from PrayerOffline"
            )
            logger.info(f"Share dua: {dua['id']}")
            self.page.snack_bar = ft.SnackBar(ft.Text("Dua copied to clipboard"))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"Failed to share dua: {e}")

    def _play_dua_audio(self, dua_id: str):
        if not self.audio:
            return
        try:
            logger.info(f"Playing audio for dua: {dua_id}")
            self.page.snack_bar = ft.SnackBar(ft.Text("Playing audio..."))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"Failed to play dua audio: {e}")

    def _create_category_tabs(self) -> ft.Row:
        """Create category selection tabs with theme"""
        tabs = []
        
        # NEW - Get theme colors
        if self.theme_manager:
            theme = self.theme_manager.get_theme()
            primary_color = theme.colors.primary
            outline_color = theme.colors.divider
        else:
            primary_color = ft.colors.PRIMARY
            outline_color = ft.colors.OUTLINE
        
        for cat_key, cat_info in self.CATEGORIES.items():
            is_selected = cat_key == self.current_category
            
            def make_click_handler(cat):
                def handler(e):
                    self._on_category_change(cat)
                    new_tabs = self._create_category_tabs()
                    self.category_tabs_container.content = new_tabs
                    self.page.update()
                return handler
            
            tab = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=cat_info["icon"],
                            size=18,
                            color=primary_color if is_selected else outline_color  # NEW - Themed
                        ),
                        ft.Text(
                            cat_info["label"],
                            size=12,
                            weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL,
                            color=primary_color if is_selected else outline_color  # NEW - Themed
                        )
                    ],
                    spacing=6
                ),
                padding=8,
                bgcolor=ft.colors.with_opacity(0.1, primary_color) if is_selected else None,  # NEW - Themed
                border_radius=8,
                border=ft.border.all(2, primary_color) if is_selected else ft.border.all(1, outline_color),  # NEW - Themed
                on_click=make_click_handler(cat_key)
            )
            tabs.append(tab)
        
        return ft.Row(controls=tabs, scroll=ft.ScrollMode.AUTO, spacing=8)

    def build(self) -> ft.Container:
        """Build the complete dua view with theme"""
        
        # NEW - Get theme text style if available
        title_style = {}
        if self.theme_manager:
            title_style = self.theme_manager.get_text_style("title")
        else:
            title_style = {"size": 24, "weight": ft.FontWeight.BOLD}
        
        self.search_field = ft.TextField(
            label="Search duas",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            border_color=ft.colors.OUTLINE,
            filled=True
        )
        
        self.category_tabs_container = ft.Container(
            content=self._create_category_tabs(),
            padding=ft.padding.symmetric(horizontal=16, vertical=8)
        )
        
        self.duas_container = ft.Column(spacing=4, expand=True)
        duas_scroll = ft.ListView(
            controls=[self.duas_container],
            expand=True,
            spacing=0,
            padding=0
        )
        
        main_column = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Duas & Supplications", **title_style),  # NEW - Themed
                    padding=16
                ),
                ft.Container(
                    content=self.search_field,
                    padding=ft.padding.symmetric(horizontal=16)
                ),
                self.category_tabs_container,
                ft.Container(
                    content=duas_scroll,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=16)
                )
            ],
            expand=True,
            spacing=0
        )
        
        self.view = ft.Container(content=main_column, expand=True)
        self._update_duas_display()
        return self.view

    def get_view(self) -> ft.Container:
        """Get the built view for integration"""
        return self.view