import pandas as pd
from datetime import datetime
from app.database import SessionLocal
from app.models import Flight, Airline, Airport
from app.weather import get_weather_for_airport

def airline_delay_rate(airline_id, db):
    total_flights = db.query(Flight).filter_by(airline_id=airline_id).count()
    if total_flights == 0:
        return 0.0
    delayed_flights = db.query(Flight).filter_by(airline_id=airline_id, is_delayed=1).count()
    return delayed_flights / total_flights

def route_delay_rate(dep_airport_id, arr_airport_id, db):
    total_flights = db.query(Flight).filter_by(departure_airport_id=dep_airport_id, arrival_airport_id=arr_airport_id).count()
    if total_flights == 0:
        return 0.0
    delayed_flights = db.query(Flight).filter_by(departure_airport_id=dep_airport_id, arrival_airport_id=arr_airport_id, is_delayed=1).count()
    return delayed_flights / total_flights

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

def create_features_for_flight(flight_id):
    db = SessionLocal()
    try:
        flight = db.query(Flight).filter_by(id=flight_id).first()
        if not flight:
            return None
        # Basic flight features
        features = {}
        features["flight_id"] = flight.id
        features["flight_number"] = flight.flight_number
        features["airline_code"] = flight.airline.code
        features["departure_airport_code"] = flight.departure_airport.code
        features["arrival_airport_code"] = flight.arrival_airport.code
        features["is_delayed"] = flight.is_delayed
        # Time features
        if flight.scheduled_departure:
            time_features = extract_time_features(flight.scheduled_departure)
            features.update(time_features)
        # Weather features
        weather = get_weather_for_airport(flight.departure_airport.code, db)
        if weather:
            features["dep_temperature"] = weather["temperature"]
            features["dep_wind_speed"] = weather["wind_speed"]
            features["dep_visibility"] = weather["visibility"]
            features["dep_humidity"] = weather["humidity"]
        features["airline_delay_rate"] = airline_delay_rate(flight.airline_id, db)
        features["route_delay_rate"] = route_delay_rate(flight.departure_airport_id, flight.arrival_airport_id, db)
        return features
    
    finally:
        db.close()

def create_features_for_all_flights():
    db = SessionLocal()
    try:
        flights = db.query(Flight).all()
        all_features = []
        for flight in flights:
            features = create_features_for_flight(flight.id)
            if features:
                all_features.append(features)

        df = pd.DataFrame(all_features)
        print(f"\nCreated features DataFrame with shape: {df.shape}")
        return df
    finally:
        db.close()

if __name__ == "__main__":
    df = create_features_for_all_flights()
    df.to_csv("flight_features.csv", index=False)


