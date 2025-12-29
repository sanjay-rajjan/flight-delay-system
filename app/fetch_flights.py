import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models import Flight, Airline, Airport


load_dotenv()
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

def fetch_flights():

    print("Fetching flight data")
    url = "http://api.aviationstack.com/v1/flights"
    params = {"access_key": API_KEY, "limit": 100}
    db = None

    try:
        print("Fetching flights from AviationStack API")
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        flights_data = data.get("data", [])
        db = SessionLocal()
        added_count = 0
        skipped_count = 0

        for flight_data in flights_data:
            flight_number = flight_data.get("flight", {}).get("iata")
            airline_code = flight_data.get("airline", {}).get("iata")
            dep_airport_code = flight_data.get("departure", {}).get("iata")
            arr_airport_code = flight_data.get("arrival", {}).get("iata")
            scheduled_dep = flight_data.get("departure", {}).get("scheduled")
            scheduled_arr = flight_data.get("arrival", {}).get("scheduled")
            
            if not all([flight_number, airline_code, dep_airport_code, arr_airport_code]):
                skipped_count += 1
                continue

            
            airline = db.query(Airline).filter_by(code=airline_code).first()
            if not airline:
                skipped_count += 1
                continue
            airline_id = airline.id

            dep_airport = db.query(Airport).filter_by(code=dep_airport_code).first()
            arr_airport = db.query(Airport).filter_by(code=arr_airport_code).first()
            
            if not dep_airport or not arr_airport:
                skipped_count += 1
                continue
            
            dep_airport_id = dep_airport.id
            arr_airport_id = arr_airport.id

            scheduled_departure = None
            scheduled_arrival = None
            
            if scheduled_dep:
                try:
                    scheduled_departure = datetime.fromisoformat(scheduled_dep.replace("Z", "+00:00"))
                except ValueError:
                    pass
            
            if scheduled_arr:
                try:
                    scheduled_arrival = datetime.fromisoformat(scheduled_arr.replace("Z", "+00:00"))
                except ValueError:
                    pass
            
            actual_dep = flight_data.get("departure", {}).get("actual")
            actual_arr = flight_data.get("arrival", {}).get("actual")

            actual_departure = None
            actual_arrival = None
            delay_minutes = 0
            is_delayed = 0

            if actual_dep:
                try:
                    actual_departure = datetime.fromisoformat(actual_dep.replace("Z", "+00:00"))
                except ValueError:
                    pass

            if actual_arr:
                try:
                    actual_arrival = datetime.fromisoformat(actual_arr.replace("Z", "+00:00"))
                except ValueError:
                    pass
            
            if scheduled_departure and actual_departure:
                delay_delta = actual_departure - scheduled_departure
                delay_minutes = int(delay_delta.total_seconds() / 60)
                is_delayed = 1 if delay_minutes > 15 else 0

            new_flight = Flight(
                flight_number=flight_number,
                airline_id=airline_id,
                departure_airport_id=dep_airport_id,
                arrival_airport_id=arr_airport_id,
                scheduled_departure=scheduled_departure,
                scheduled_arrival=scheduled_arrival,
                actual_departure=actual_departure,
                actual_arrival=actual_arrival,
                delay_minutes=delay_minutes,
                is_delayed=is_delayed
            )
            db.add(new_flight)
            added_count += 1
        db.commit()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except Exception as e:
        print(f"Error processing flights: {e}")
    finally:
        if db:
            db.close()
            print("Database session closed.")

if __name__ == "__main__":
    fetch_flights()



