from src.common.text_utils import normalize_area, normalize_text, extract_temperatures


def test_normalize_text():
    assert normalize_text("A  test\nvalue  36 C") == "A test value 36°C"


def test_normalize_area():
    assert normalize_area("Living") == "living room"


def test_extract_temperatures():
    assert extract_temperatures("Peak temp 45.6 C") == [45.6]
