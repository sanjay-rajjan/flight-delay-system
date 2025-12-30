import pickle
from datetime import datetime
from app.models import Airport, Airline, Flight
from app.database import SessionLocal
from app.weather import get_weather_for_airport

with open("flight_delay_model.pkl", "rb") as file:
    model = pickle.load(file)

def extract_time_features(dt):
    if not dt:
        return {}
    return {
        "hour": dt.hour,
        "day_of_week": dt.weekday(),
        "month": dt.month,
        "is_weekend": 1 if dt.weekday() >= 5 else 0,
        "is_morning": 1 if 6 <= dt.hour < 12 else 0,
        "is_afternoon": 1 if 12 <= dt.hour < 18 else 0,
        "is_evening": 1 if 18 <= dt.hour < 24 else 0,
        "is_night": 1 if dt.hour < 6 else 0
    }

def calculate_airline_delay_rate(airline_id, db):
    total = db.query(Flight).filter_by(airline_id=airline_id).count()
    if total == 0:
        return 0.0
    delayed = db.query(Flight).filter_by(airline_id=airline_id, is_delayed=1).count()
    return delayed / total

def calculate_route_delay_rate(dep_airport_id, arr_airport_id, db):
    total = db.query(Flight).filter_by(departure_airport_id=dep_airport_id, arrival_airport_id=arr_airport_id).count()
    if total == 0:
        return 0.0
    delayed = db.query(Flight).filter_by(departure_airport_id=dep_airport_id, arrival_airport_id=arr_airport_id, is_delayed=1).count()
    return delayed / total

def predict_delay(airline_code, departure_airport_code, arrival_airport_code, scheduled_departure):
    db = SessionLocal()
    try:
        time_features = extract_time_features(scheduled_departure)
        
        airline = db.query(Airline).filter_by(code=airline_code).first()
        if not airline:
            raise ValueError(f"Airline {airline_code} not found")
        
        airline_delay = calculate_airline_delay_rate(airline.id, db)
        
        dep_airport = db.query(Airport).filter_by(code=departure_airport_code).first()
        arr_airport = db.query(Airport).filter_by(code=arrival_airport_code).first()
        
        if not dep_airport:
            raise ValueError(f"Departure airport {departure_airport_code} not found")
        if not arr_airport:
            raise ValueError(f"Arrival airport {arrival_airport_code} not found")
        
        route_delay = calculate_route_delay_rate(dep_airport.id, arr_airport.id, db)
        
        try:
            weather = get_weather_for_airport(departure_airport_code, db)
            temp = weather.get("temperature", 70.0) if weather else 70.0
            wind = weather.get("wind_speed", 10.0) if weather else 10.0
            visibility = weather.get("visibility", 10.0) if weather else 10.0
            humidity = weather.get("humidity", 50.0) if weather else 50.0
        except:
            temp = 70.0
            wind = 10.0
            visibility = 10.0
            humidity = 50.0
        
        features = [
            time_features["hour"],
            time_features["day_of_week"],
            time_features["month"],
            time_features["is_weekend"],
            time_features["is_morning"],
            time_features["is_afternoon"],
            time_features["is_evening"],
            time_features["is_night"],
            temp,
            wind,
            visibility,
            humidity,
            airline_delay,
            route_delay
        ]
        
        pred = model.predict([features])[0]
        prediction = "delayed" if pred == 1 else "on-time"
        probability = model.predict_proba([features])[0][1]
        
        if probability > 0.7 or probability < 0.3:
            confidence = "high"
        elif probability > 0.6 or probability < 0.4:
            confidence = "medium"
        else:
            confidence = "low"
        
        return prediction, probability, confidence
        
    finally:
        db.close()