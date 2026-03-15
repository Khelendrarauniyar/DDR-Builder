from __future__ import annotations

import re


AREA_ALIASES = {
    "living": "living room",
    "living room": "living room",
    "hall": "hallway",
    "corridor": "hallway",
    "kitchen": "kitchen",
    "bathroom": "bathroom",
    "bedroom": "bedroom",
    "roof": "roof",
    "ceiling": "ceiling",
    "wall": "wall",
}


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_temperature_units(text: str) -> str:
    text = text.replace("° C", "°C").replace(" deg C", "°C").replace(" C", "°C")
    text = text.replace("celsius", "°C").replace("Celsius", "°C")
    return text


def normalize_text(text: str) -> str:
    return normalize_temperature_units(normalize_whitespace(text))


def normalize_area(area: str) -> str:
    a = normalize_text(area).lower()
    for key, value in AREA_ALIASES.items():
        if key in a:
            return value
    return a


def extract_temperatures(text: str) -> list[float]:
    matches = re.findall(r"(-?\d+(?:\.\d+)?)\s*°?\s*[Cc]", text)
    return [float(m) for m in matches]
