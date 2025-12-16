"""
geocode.py
-----------
Utility functions for converting place names to coordinates (latitude, longitude)
used by Gfetchert.
"""

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

# Simple cache to avoid redundant lookups
_GEOCODE_CACHE = {}


def get_coordinates(place_name: str) -> tuple[float, float, str]:
    """
    Convert a place name (city, district, or region) into geographic coordinates.

    Parameters
    ----------
    place_name : str
        Name of the location (e.g., "Dehradun, Uttarakhand" or "Nainital, India")

    Returns
    -------
    tuple
        (latitude, longitude, resolved_name)

    Raises
    ------
    ValueError
        If the place could not be found or geocoding failed.
    """
    if not place_name or not isinstance(place_name, str):
        raise ValueError("Place name must be a non-empty string.")

    # Return cached result if already queried
    if place_name in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[place_name]

    try:
        geolocator = Nominatim(user_agent="gfetchert-geocoder")
        location = geolocator.geocode(place_name, timeout=15)

        if not location:
            raise ValueError(f"Location '{place_name}' not found.")

        lat, lon, resolved = location.latitude, location.longitude, location.address

        # Cache the result for reuse
        _GEOCODE_CACHE[place_name] = (lat, lon, resolved)
        return lat, lon, resolved

    except (GeocoderUnavailable, GeocoderTimedOut):
        raise ConnectionError("Geocoding service unavailable or timed out.")
    except Exception as e:
        raise ValueError(f"Geocoding failed for '{place_name}': {e}")
