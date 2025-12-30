import pandas as pd
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Flight, Airline, Airport

def import_flights(csv_path="data/flights.csv", limit=10000):
    df = pd.read_csv(csv_path, nrows=limit)
    db = SessionLocal()
    airlines = db.query(Airline).all()
    airline_lookup = {a.code: a.id for a in airlines}
    airports = db.query(Airport).all()
    airport_lookup = {a.code: a.id for a in airports}
    added = 0

    for index, row in df.iterrows():
        airline_code = row.get("AIRLINE")
        dep_code = row.get("ORIGIN_AIRPORT")
        arr_code = row.get("DESTINATION_AIRPORT")
        if pd.isna(airline_code) or pd.isna(dep_code) or pd.isna(arr_code):
            continue

        airline_id = airline_lookup.get(airline_code)
        dep_id = airport_lookup.get(dep_code)
        arr_id = airport_lookup.get(arr_code)
        if not airline_id or not dep_id or not arr_id:
            continue
        year = int(row.get("YEAR", 2015))
        month = int(row.get("MONTH", 1))
        day = int(row.get("DAY", 1))
        scheduled_dep_time = row.get("SCHEDULED_DEPARTURE")
        if pd.isna(scheduled_dep_time):
            skipped_count += 1
            continue
        scheduled_dep_time = int(scheduled_dep_time)
        hour = scheduled_dep_time // 100
        minute = scheduled_dep_time % 100
        if hour >= 24:
            hour = 0
            day += 1
        try:
            scheduled_departure = datetime(year, month, day, hour, minute)
        except ValueError:
            continue
        departure_delay = row.get('DEPARTURE_DELAY', 0)
        
        if pd.isna(departure_delay):
            departure_delay = 0
        else:
            departure_delay = int(departure_delay)
        actual_departure = scheduled_departure + timedelta(minutes=departure_delay)
        is_delayed = 1 if departure_delay > 15 else 0
        flight_number = row.get("FLIGHT_NUMBER", "UNKNOWN")
        if pd.isna(flight_number):
            flight_number = "UNKNOWN"
        else:
            flight_number = str(int(flight_number))

        flight = Flight(
            flight_number=flight_number[:10],
            airline_id=airline_id,
            departure_airport_id=dep_id,
            arrival_airport_id=arr_id,
            scheduled_departure=scheduled_departure,
            actual_departure=actual_departure,
            actual_arrival=None,
            delay_minutes=departure_delay,
            is_delayed=is_delayed
        )
        db.add(flight)
        added += 1
        # Commit every 1000 flights
        if added % 1000 == 0:
            db.commit()
            
    db.commit()
    db.close()

if __name__ == "__main__":
    import_flights()