import pytest

# Ensure flet is available before importing theme_manager (theme_manager depends on flet)
pytest.importorskip("flet")

from theme_manager import initialize_theme_manager, get_theme_manager


def test_singleton_instance():
	"""initialize_theme_manager() and get_theme_manager() should return the same singleton."""
	a = initialize_theme_manager()
	b = get_theme_manager()
	assert a is b


def test_get_all_themes_contains_spiritual_light():
	tm = get_theme_manager()
	themes = tm.get_all_themes()
	assert isinstance(themes, list)
	assert "spiritual_light" in themes


def test_get_color_alias_and_direct():
	tm = get_theme_manager()
	# direct lookup
	primary = tm.get_color("primary")
	assert isinstance(primary, str) and primary.startswith("#")
	# alias fallback
	bg = tm.get_color("bg")
	background = tm.get_color("background")
	assert bg == background


def test_get_gradient_for_prayer():
	tm = get_theme_manager()
	grad = tm.get_gradient("fajr")
	# ft.LinearGradient has a 'colors' attribute containing color strings
	assert hasattr(grad, "colors")
	assert len(grad.colors) >= 2


def test_style_generators_return_expected_keys():
	tm = get_theme_manager()
	card = tm.get_card_style(elevated=True, glass=False)
	assert isinstance(card, dict)
	assert "bgcolor" in card

	btn = tm.get_button_style(variant="filled")
	assert isinstance(btn, dict)
	assert "bgcolor" in btn


if __name__ == "__main__":
	# Allow running this test file directly
	raise SystemExit(pytest.main([__file__]))