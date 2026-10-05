import json
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime

WEATHER_CODES = {
    0: "clear sky", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "freezing fog",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    56: "freezing drizzle", 57: "heavy freezing drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    66: "freezing rain", 67: "heavy freezing rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
    80: "light rain showers", 81: "rain showers", 82: "violent rain showers",
    85: "snow showers", 86: "heavy snow showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "heavy thunderstorm with hail",
}


def _get_json(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def get_datetime() -> str:
    """Get the current local date, weekday and time on the user's PC."""
    return datetime.now().strftime("%A, %d %B %Y, %H:%M")


def get_weather(city: str) -> str:
    """Get the current weather and today's forecast for a city.

    Args:
        city: City name, e.g. 'Berlin' or 'Ingolstadt'.
    """
    city = city.strip()
    if not city:
        return "No city given."
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
            {"name": city, "count": 1, "language": "en"}
        )
        results = _get_json(geo_url).get("results")
        if not results:
            return f"Couldn't find a place called {city}."
        place = results[0]

        forecast_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(
            {
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 1,
            }
        )
        data = _get_json(forecast_url)
        cur = data["current"]
        day = data["daily"]
        desc = WEATHER_CODES.get(cur["weather_code"], "unknown conditions")
        return (
            f"{place['name']}, {place.get('country', '')}: {desc}, "
            f"{cur['temperature_2m']} C (feels like {cur['apparent_temperature']} C), "
            f"wind {cur['wind_speed_10m']} km/h. "
            f"Today: high {day['temperature_2m_max'][0]} C, "
            f"low {day['temperature_2m_min'][0]} C, "
            f"rain chance {day['precipitation_probability_max'][0]}%."
        )
    except Exception as e:
        return f"Weather lookup failed: {e}"


def open_website(url: str) -> str:
    """Open a website in the user's default browser. To search the web, open
    https://www.google.com/search?q=<search terms> instead.

    Args:
        url: The address, e.g. 'youtube.com' or 'https://github.com'.
    """
    url = url.strip()
    if not url:
        return "No URL given."
    if "://" not in url:
        url = "https://" + url
    if not url.lower().startswith(("http://", "https://")):
        return "Only http and https links are allowed."
    webbrowser.open(url)
    return f"Opened {url}"