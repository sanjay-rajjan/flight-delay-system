import requests
import os
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_for_airport(airport_code, db):
    from app.models import Airport
    airport = db.query(Airport).filter_by(code=airport_code).first()
    if not airport or not airport.city:
        return None
    
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{airport.city},{airport.country}",
        "appid": WEATHER_API_KEY,
        "units": "imperial"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        weather = {
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "visibility": data.get("visibility", 10000) / 1000,  # Convert to km
            "conditions": data["weather"][0]["main"],
            "description": data["weather"][0]["description"]
        }
        return weather
    
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None
