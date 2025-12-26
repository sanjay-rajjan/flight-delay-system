import requests
import os
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models import Airport

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

def fetch_airports():
    print("Starting airport data fetch")
    url = "http://api.aviationstack.com/v1/airports"
    params = {"access_key": API_KEY, "limit": 100}
    db = None
    try:
        print("Fetching airports from AviationStack API")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        airports_data = data.get('data', [])
        print(f"Received {len(airports_data)} airports from API")

        db = SessionLocal()
        added_count = 0
        skipped_count = 0
        
        for airport_data in airports_data:
            # Fields from API response
            code = airport_data.get('iata_code')
            name = airport_data.get('airport_name')
            if not code or not name:
                skipped_count += 1
                continue
            city = airport_data.get('city_name')
            country = airport_data.get('country_name')
            existing = db.query(Airport).filter_by(code=code).first()
            if existing:
                skipped_count += 1
                continue

            new_airport = Airport(
                code=code, name=name,
                city=city if city else "Unknown",
                country=country if country else "Unknown" )
            db.add(new_airport)
            added_count += 1
        
        db.commit()
        print(f"\n Successfully added {added_count} airports")
        print(f" Skipped {skipped_count} airports (duplicates or missing data)")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except Exception as e:
        print(f"Error processing airports: {e}")
    finally:
        if db:
            db.close()
            print("Database session closed.")
    
if __name__ == "__main__":
    fetch_airports()