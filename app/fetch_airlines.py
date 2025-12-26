import requests
import os
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models import Airline

load_dotenv()
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

def fetch_airlines():
    print("Starting airline data fetch")
    url = "http://api.aviationstack.com/v1/airlines"
    params = {
        'access_key': API_KEY,
        'limit': 100
    }
    db = None
    
    try:
        print("Fetching airlines from AviationStack API")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        airlines_data = data.get('data', [])
        
        print(f"Received {len(airlines_data)} airlines from API")
        
        db = SessionLocal()
        added_count = 0
        skipped_count = 0
        
        for airline_data in airlines_data:
            code = airline_data.get('iata_code')
            name = airline_data.get('airline_name')
            if not code or not name:
                skipped_count += 1
                continue
            existing = db.query(Airline).filter_by(code=code).first()
            if existing:
                skipped_count += 1
                continue
            new_airline = Airline(code=code, name=name)
            db.add(new_airline)
            added_count += 1
        
        db.commit()
        print(f"\nSuccessfully added {added_count} airlines")
        print(f"Skipped {skipped_count} airlines (duplicates or missing data)")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except Exception as e:
        print(f"Error processing airlines: {e}")

    finally:
        if db:
            db.close()
            print("Database session closed.")

if __name__ == "__main__":
    fetch_airlines()