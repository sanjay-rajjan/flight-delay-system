import pandas as pd
from datetime import datetime
from app.database import SessionLocal
from app.models import Flight

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

def create_features_for_all_flights():
    db = SessionLocal()
    try:
        flights = db.query(Flight).all()
        airline_stats = {}
        for flight in flights:
            if flight.airline_id not in airline_stats:
                airline_stats[flight.airline_id] = {"total": 0, "delayed": 0}
            airline_stats[flight.airline_id]["total"] += 1
            if flight.is_delayed:
                airline_stats[flight.airline_id]["delayed"] += 1
        airline_delay_rates = {
            aid: stats["delayed"] / stats["total"] if stats["total"] > 0 else 0.0
            for aid, stats in airline_stats.items()
        }
        route_stats = {}
        for flight in flights:
            route = (flight.departure_airport_id, flight.arrival_airport_id)
            if route not in route_stats:
                route_stats[route] = {"total": 0, "delayed": 0}
            route_stats[route]["total"] += 1
            if flight.is_delayed:
                route_stats[route]["delayed"] += 1
        route_delay_rates = {
            route: stats["delayed"] / stats["total"] if stats["total"] > 0 else 0.0
            for route, stats in route_stats.items()
        }
        
        all_features = []
        
        for i, flight in enumerate(flights):
            features = {}
            features["flight_id"] = flight.id
            features["flight_number"] = flight.flight_number
            features["airline_code"] = flight.airline.code
            features["departure_airport_code"] = flight.departure_airport.code
            features["arrival_airport_code"] = flight.arrival_airport.code
            features["is_delayed"] = flight.is_delayed
            if flight.scheduled_departure:
                time_features = extract_time_features(flight.scheduled_departure)
                features.update(time_features)

            features["dep_temperature"] = 70
            features["dep_wind_speed"] = 10
            features["dep_visibility"] = 10
            features["dep_humidity"] = 50
            
            features["airline_delay_rate"] = airline_delay_rates.get(flight.airline_id, 0.0)
            route = (flight.departure_airport_id, flight.arrival_airport_id)
            features["route_delay_rate"] = route_delay_rates.get(route, 0.0)
            
            all_features.append(features)
        
        df = pd.DataFrame(all_features)
        return df
        
    finally:
        db.close()

if __name__ == "__main__":
    df = create_features_for_all_flights()
    df.to_csv("flight_features.csv", index=False)