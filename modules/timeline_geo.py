import re
import dateparser
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="semantic_pipeline")


def extract_dates(text: str):
    """
    Extract well-formed dates only.
    Avoid false positives like standalone years or today's date.
    """
    dates = []
    # Match "28 August 1929" or "August 28, 1929"
    patterns = [
        r"\b\d{1,2}\s+\w+\s+\d{4}\b",   # 28 August 1929
        r"\b\w+\s+\d{1,2},\s*\d{4}\b"   # August 28, 1929
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            parsed = dateparser.parse(match)
            if parsed:
                dates.append(str(parsed.date()))

    return list(set(dates))  # unique only


def geocode_place(place: str):
    """Convert a place name into coordinates (lat/lon)."""
    try:
        loc = geolocator.geocode(place)
        if loc:
            return {
                "place": place,
                "coordinates": {"lat": loc.latitude, "lon": loc.longitude},
            }
    except Exception:
        return None
