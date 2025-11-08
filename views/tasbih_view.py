"""
Advanced Tasbih Counter View - WITH THEME SUPPORT
Added theme_manager parameter and themed styling
"""

import flet as ft
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class DhikrCounter:
    """Individual dhikr counter with history tracking"""
    
    def __init__(self, name: str, arabic: str, target: int = 33):
        self.name = name
        self.arabic = arabic
        self.target = target
        self.current_count = 0
        self.sessions = []
        self.started_at = None

    def increment(self) -> None:
        self.current_count += 1
        if self.started_at is None:
            self.started_at = datetime.now()

    def reset(self) -> None:
        if self.current_count > 0:
            session = {
                "count": self.current_count,
                "target": self.target,
                "timestamp": self.started_at.isoformat() if self.started_at else datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.started_at).total_seconds() if self.started_at else 0
            }
            self.sessions.append(session)
        self.current_count = 0
        self.started_at = None

    def set_target(self, new_target: int) -> None:
        self.target = new_target

    def get_progress_percent(self) -> float:
        if self.target <= 0:
            return 0
        return min(100, (self.current_count / self.target) * 100)

    def is_target_reached(self) -> bool:
        return self.current_count >= self.target

    def get_daily_stats(self) -> Dict:
        today = datetime.now().date()
        today_sessions = [
            s for s in self.sessions
            if datetime.fromisoformat(s["timestamp"]).date() == today
        ]
        return {
            "sessions_count": len(today_sessions),
            "total_count": sum(s["count"] for s in today_sessions),
            "total_time": sum(s["duration_seconds"] for s in today_sessions)
        }

    def get_weekly_stats(self) -> Dict:
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_sessions = [
            s for s in self.sessions
            if week_start <= datetime.fromisoformat(s["timestamp"]).date() <= week_end
        ]
        return {
            "sessions_count": len(week_sessions),
            "total_count": sum(s["count"] for s in week_sessions),
            "total_time": sum(s["duration_seconds"] for s in week_sessions),
            "average_per_session": sum(s["count"] for s in week_sessions) / len(week_sessions) if week_sessions else 0
        }

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "arabic": self.arabic,
            "target": self.target,
            "current_count": self.current_count,
            "sessions": self.sessions,
            "started_at": self.started_at.isoformat() if self.started_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DhikrCounter":
        counter = cls(data["name"], data["arabic"], data["target"])
        counter.current_count = data.get("current_count", 0)
        counter.sessions = data.get("sessions", [])
        if data.get("started_at"):
            counter.started_at = datetime.fromisoformat(data["started_at"])
        return counter


class TasbihView:
    """Advanced Tasbih counter with theme support"""
    
    DEFAULT_DHIKRS = [
        {"name": "Subhanallah", "arabic": "سبحان الله", "transliteration": "Glory be to Allah", "target": 33},
        {"name": "Alhamdulillah", "arabic": "الحمد لله", "transliteration": "Praise be to Allah", "target": 33},
        {"name": "Allahu Akbar", "arabic": "الله أكبر", "transliteration": "Allah is the Greatest", "target": 33},
        {"name": "La ilaha illallah", "arabic": "لا إله إلا الله", "transliteration": "There is no deity except Allah", "target": 100}
    ]
    
    TARGET_PRESETS = [33, 99, 100, 1000]
    
    def __init__(
        self,
        page: ft.Page,
        storage_service,
        audio_service=None,
        theme_manager=None,  # NEW - Added theme_manager
        on_counter_change: Optional[Callable] = None,
        i18n_strings: Dict = None
    ):
        """Initialize Tasbih View with theme support"""
        self.page = page
        self.storage = storage_service
        self.audio = audio_service
        self.theme_manager = theme_manager  # NEW - Store theme_manager
        self.on_counter_change = on_counter_change
        self.strings = i18n_strings or {}
        
        self.counters: Dict[str, DhikrCounter] = {}
        self.current_dhikr_index = 0
        self.vibration_enabled = True
        self.sound_enabled = True
        
        self._initialize_counters()
        
        self.dhikr_display = None
        self.count_display = None
        self.progress_indicator = None
        self.stats_text = None

    def _initialize_counters(self):
        """Initialize or load counters from storage"""
        try:
            saved_data = self.storage.get("tasbih_counters", None)
            if saved_data:
                for dhikr_data in saved_data:
                    counter = DhikrCounter.from_dict(dhikr_data)
                    self.counters[counter.name] = counter
                logger.info(f"Loaded {len(self.counters)} counters from storage")
            else:
                for dhikr in self.DEFAULT_DHIKRS:
                    self.counters[dhikr["name"]] = DhikrCounter(
                        dhikr["name"], dhikr["arabic"], dhikr["target"]
                    )
                logger.info("Initialized default counters")
        except Exception as e:
            logger.error(f"Failed to initialize counters: {e}")
            for dhikr in self.DEFAULT_DHIKRS:
                self.counters[dhikr["name"]] = DhikrCounter(
                    dhikr["name"], dhikr["arabic"], dhikr["target"]
                )

    def _save_counters(self):
        try:
            data = [counter.to_dict() for counter in self.counters.values()]
            self.storage.set("tasbih_counters", data)
            logger.info("Counters saved to storage")
        except Exception as e:
            logger.error(f"Failed to save counters: {e}")

    def _get_current_counter(self) -> Optional[DhikrCounter]:
        counter_names = list(self.counters.keys())
        if not counter_names:
            return None
        return self.counters[counter_names[self.current_dhikr_index]]

    def _increment_counter(self, e=None):
        counter = self._get_current_counter()
        if counter:
            counter.increment()
            self._save_counters()
            self._play_sound_feedback()
            self._play_vibration_feedback()
            self._update_display()
            if self.on_counter_change:
                self.on_counter_change(counter)
            if counter.is_target_reached():
                self._show_target_celebration()

    def _reset_current_counter(self, e=None, confirmed: bool = False):
        counter = self._get_current_counter()
        if not counter:
            return
        if not confirmed:
            self._show_reset_confirmation()
        else:
            counter.reset()
            self._save_counters()
            self._update_display()

    def _show_reset_confirmation(self):
        counter = self._get_current_counter()
        def close_dialog(dlg):
            dlg.open = False
            self.page.update()
        def reset_and_close(dlg):
            self._reset_current_counter(confirmed=True)
            close_dialog(dlg)
        
        dlg = ft.AlertDialog(
            title=ft.Text("Reset Counter?"),
            content=ft.Column(
                controls=[
                    ft.Text(f"{counter.name}: {counter.current_count}/{counter.target}"),
                    ft.Text("This action cannot be undone.", color=ft.colors.ERROR)
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda x: close_dialog(dlg)),
                ft.TextButton("Reset", style=ft.ButtonStyle(color=ft.colors.ERROR), on_click=lambda x: reset_and_close(dlg))
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _switch_to_next_dhikr(self, e=None):
        self.current_dhikr_index = (self.current_dhikr_index + 1) % len(self.counters)
        self._update_display()

    def _switch_to_prev_dhikr(self, e=None):
        self.current_dhikr_index = (self.current_dhikr_index - 1) % len(self.counters)
        self._update_display()

    def _play_sound_feedback(self):
        if self.sound_enabled and self.audio:
            try:
                self.audio.play_notification()
            except Exception as e:
                logger.debug(f"Sound feedback failed: {e}")

    def _play_vibration_feedback(self):
        if self.vibration_enabled:
            try:
                logger.debug("Vibration feedback triggered")
            except Exception as e:
                logger.debug(f"Vibration feedback failed: {e}")

    def _show_target_celebration(self):
        # NEW - Use theme colors if available
        icon_color = ft.colors.PRIMARY
        if self.theme_manager:
            theme = self.theme_manager.get_theme()
            icon_color = theme.colors.primary
        
        snackbar = ft.SnackBar(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.icons.CELEBRATION, color=icon_color),
                    ft.Text("Target Reached!", size=16)
                ],
                spacing=8
            )
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()

    def _set_custom_target(self, new_target: int):
        counter = self._get_current_counter()
        if counter:
            counter.set_target(new_target)
            self._save_counters()
            self._update_display()

    def _update_display(self):
        counter = self._get_current_counter()
        if not counter:
            return
        if self.dhikr_display:
            self.dhikr_display.value = counter.arabic
        if self.count_display:
            self.count_display.value = f"{counter.current_count}/{counter.target}"
        if self.progress_indicator:
            self.progress_indicator.value = counter.get_progress_percent() / 100
        self._update_stats_display()
        self.page.update()

    def _update_stats_display(self):
        counter = self._get_current_counter()
        if not counter or not self.stats_text:
            return
        daily = counter.get_daily_stats()
        weekly = counter.get_weekly_stats()
        stats_content = (
            f"Today: {daily['sessions_count']} sessions, {daily['total_count']} total\n"
            f"This Week: {weekly['sessions_count']} sessions, {weekly['total_count']} total"
        )
        self.stats_text.value = stats_content

    def _create_counter_card(self) -> ft.Container:
        """Create main counter display card with theme"""
        counter = self._get_current_counter()
        
        # NEW - Get theme colors
        if self.theme_manager:
            theme = self.theme_manager.get_theme()
            primary_color = theme.colors.primary
            surface_color = theme.colors.surface
            on_surface_color = theme.colors.on_surface
        else:
            primary_color = ft.colors.PRIMARY
            surface_color = ft.colors.SURFACE_VARIANT
            on_surface_color = ft.colors.ON_SURFACE
        
        self.dhikr_display = ft.Text(
            value=counter.arabic if counter else "",
            size=36,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            color=primary_color  # NEW - Themed
        )
        
        self.count_display = ft.Text(
            value=f"{counter.current_count if counter else 0}/{counter.target if counter else 0}",
            size=48,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            color=on_surface_color  # NEW - Themed
        )
        
        self.progress_indicator = ft.ProgressRing(
            value=counter.get_progress_percent() / 100 if counter else 0,
            stroke_width=8,
            width=200,
            height=200,
            color=primary_color  # NEW - Themed
        )
        
        progress_stack = ft.Stack(
            controls=[
                self.progress_indicator,
                ft.Container(
                    content=self.count_display,
                    alignment=ft.alignment.center,
                    width=200,
                    height=200
                )
            ],
            width=200,
            height=200
        )
        
        increment_btn = ft.IconButton(
            icon=ft.icons.ADD_CIRCLE,
            icon_size=80,
            icon_color=primary_color,  # NEW - Themed
            on_click=self._increment_counter
        )
        
        reset_btn = ft.IconButton(
            icon=ft.icons.REFRESH,
            tooltip="Reset Counter",
            on_click=self._reset_current_counter
        )
        
        prev_btn = ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            tooltip="Previous Dhikr",
            on_click=self._switch_to_prev_dhikr
        )
        
        next_btn = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD,
            tooltip="Next Dhikr",
            on_click=self._switch_to_next_dhikr
        )
        
        self.stats_text = ft.Text(
            size=11,
            color=ft.colors.OUTLINE,
            text_align=ft.TextAlign.CENTER
        )

        # NEW - Use theme card style if available
        card_style = {}
        if self.theme_manager:
            card_style = self.theme_manager.get_card_style()
        else:
            card_style = {
                "padding": 16,
                "border": ft.border.all(1, ft.colors.OUTLINE),
                "border_radius": 12
            }

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=self.dhikr_display,
                        padding=16,
                        bgcolor=surface_color,  # NEW - Themed
                        border_radius=8
                    ),
                    ft.Container(
                        content=progress_stack,
                        alignment=ft.alignment.center,
                        padding=20
                    ),
                    ft.Container(
                        content=increment_btn,
                        alignment=ft.alignment.center
                    ),
                    ft.Row(
                        controls=[prev_btn, reset_btn, next_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=16
                    ),
                    ft.Container(
                        content=self.stats_text,
                        padding=12
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16
            ),
            **card_style  # NEW - Apply theme card style
        )

    def _create_target_selector(self) -> ft.Container:
        """Create target preset buttons"""
        buttons = []
        for target in self.TARGET_PRESETS:
            btn = ft.ElevatedButton(
                text=str(target),
                on_click=lambda e, t=target: self._set_custom_target(t),
                expand=True
            )
            buttons.append(btn)
        
        custom_target_field = ft.TextField(
            label="Custom Target",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100
        )
        
        def apply_custom_target(e):
            try:
                target = int(custom_target_field.value)
                if target > 0:
                    self._set_custom_target(target)
                    custom_target_field.value = ""
                    self.page.update()
            except (ValueError, AttributeError):
                pass
        
        apply_btn = ft.IconButton(icon=ft.icons.CHECK, on_click=apply_custom_target)
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Select Target", size=14, weight=ft.FontWeight.W_600),
                    ft.Row(controls=buttons, spacing=4),
                    ft.Row(controls=[custom_target_field, apply_btn], spacing=4)
                ],
                spacing=8
            ),
            padding=12,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=8
        )

    def _create_settings_section(self) -> ft.Container:
        """Create settings for sound and vibration"""
        def toggle_sound(e):
            self.sound_enabled = e.control.value
        def toggle_vibration(e):
            self.vibration_enabled = e.control.value
        
        sound_toggle = ft.Switch(value=self.sound_enabled, on_change=toggle_sound)
        vibration_toggle = ft.Switch(value=self.vibration_enabled, on_change=toggle_vibration)
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.VOLUME_UP, size=18),
                            ft.Text("Sound", expand=True),
                            sound_toggle
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.VIBRATION, size=18),
                            ft.Text("Vibration", expand=True),
                            vibration_toggle
                        ]
                    )
                ],
                spacing=8
            ),
            padding=12,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=8
        )

    def build(self):
        """Build the complete Tasbih view"""
        self._update_display()
        
        # NEW - Get theme text style if available
        title_style = {}
        if self.theme_manager:
            title_style = self.theme_manager.get_text_style("title")
        else:
            title_style = {"size": 24, "weight": ft.FontWeight.BOLD}
        
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Tasbih Counter", **title_style),  # NEW - Themed
                    padding=16
                ),
                ft.ListView(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    self._create_counter_card(),
                                    self._create_target_selector(),
                                    self._create_settings_section(),
                                    ft.Container(height=20)
                                ],
                                spacing=12
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