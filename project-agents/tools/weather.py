"""Weather tool — live weather from Open-Meteo (free, no API key).

Teaching goal: the LLM cannot know today's weather. A tool that calls a real
API gives it fresh data. Two calls: city name -> lat/lon, then lat/lon -> weather.
"""

import json
import urllib.parse
import urllib.request

from langchain_core.tools import tool

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10

WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "fog", 51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain", 71: "light snow", 73: "snow",
    75: "heavy snow", 80: "rain showers", 81: "rain showers", 82: "violent rain showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with hail",
}


def get_json(url: str, params: dict) -> dict:
    with urllib.request.urlopen(f"{url}?{urllib.parse.urlencode(params)}", timeout=TIMEOUT) as resp:
        return json.load(resp)


def get_weather(city: str) -> str:
    try:
        places = get_json(GEOCODE_URL, {"name": city, "count": 1}).get("results")
        if not places:
            return f"Error: could not find a city named '{city}'."
        place = places[0]
        current = get_json(FORECAST_URL, {
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        })["current"]
    except Exception as exc:
        return f"Error: weather lookup failed ({type(exc).__name__})."

    sky = WEATHER_CODES.get(current["weather_code"], "unknown conditions")
    return (f"{place['name']}, {place.get('country', '')}: {current['temperature_2m']}°C, {sky}, "
            f"humidity {current['relative_humidity_2m']}%, wind {current['wind_speed_10m']} km/h")


@tool
def weather(city: str) -> str:
    """Get the CURRENT weather for a city: temperature (°C), sky conditions,
    humidity and wind. Use it whenever the user asks about weather, temperature
    or rain right now. Do NOT use it for anything else.

    Input: just the city name, e.g. "Mumbai" or "London".
    """
    return get_weather(city)


if __name__ == "__main__":
    print(get_weather("Mumbai"))
