import pickle
from datetime import datetime
from app.models import Airport, Airline
from app.database import SessionLocal
from app.weather import get_weather_for_airport
from app.create_features import airline_delay_rate, route_delay_rate, extract_time_features

with open("flight_delay_model.pkl", "rb") as file:
    model = pickle.load(file)

def predict_delay(airline_code, departure_airport_code, arrival_airport_code, scheduled_departure):
    db = SessionLocal()
    try:
        time_features = extract_time_features(scheduled_departure)
        airline = db.query(Airline).filter_by(code=airline_code).first()
        airline_delay = airline_delay_rate(airline.id, db)

        dep_airport = db.query(Airport).filter_by(code=departure_airport_code).first()
        arr_airport = db.query(Airport).filter_by(code=arrival_airport_code).first()
        route_delay = route_delay_rate(dep_airport.id, arr_airport.id, db)

        weather = get_weather_for_airport(departure_airport_code, db)

        features = [
            time_features["hour"],
            time_features["day_of_week"],
            time_features["month"],
            time_features["is_weekend"],
            time_features["is_morning"],
            time_features["is_afternoon"],
            time_features["is_evening"],
            time_features["is_night"],
            # Make default weather values for if the API fails
            weather["temperature"] if weather else 70.0,
            weather["wind_speed"] if weather else 10.0,
            weather["visibility"] if weather else 10.0,
            weather["humidity"] if weather else 50.0,
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


    

