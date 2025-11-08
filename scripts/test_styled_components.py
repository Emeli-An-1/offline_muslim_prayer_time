"""Quick test for styled components

This script imports PrayerCard and CountdownWidget and creates instances
using the global theme manager created by initialize_theme_manager.
It prints summary info to confirm successful construction.
"""
from components.styled_components import PrayerCard, CountdownWidget
from theme_manager import initialize_theme_manager, get_theme_manager


class MockStorage:
    def __init__(self):
        self._data = {}
    def get(self, key, default=None):
        return self._data.get(key, default)
    def set(self, key, value):
        self._data[key] = value


def main():
    storage = MockStorage()
    theme = initialize_theme_manager(storage, "SereneLight")

    card = PrayerCard(
        prayer_name="Fajr",
        adhan_time="05:30",
        jamaat_time="05:45",
        is_next=True,
        theme_manager=theme
    )

    countdown = CountdownWidget(
        next_prayer="Dhuhr",
        time_remaining="02:15:30",
        progress=0.65,
        theme_manager=theme
    )

    print(f"PrayerCard created: {type(card)}")
    print(f"CountdownWidget created: {type(countdown)}")
    print("PrayerCard content type:", type(card.content))
    print("Countdown stack children:", len(countdown.content.controls))


if __name__ == '__main__':
    main()
