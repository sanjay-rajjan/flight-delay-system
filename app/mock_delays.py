import random
from datetime import timedelta
from app.database import SessionLocal
from app.models import Flight

def add_mock_delays():
    db = SessionLocal()
    
    try:
        flights = db.query(Flight).all()
        
        for flight in flights:
            # 30% chance of delay
            is_delayed = random.random() < 0.3
            
            if is_delayed and flight.scheduled_departure:
                # Random delay between 15-120 mins
                delay_minutes = random.randint(15, 120)
                flight.actual_departure = flight.scheduled_departure + timedelta(minutes=delay_minutes)
                if flight.scheduled_arrival:
                    flight.actual_arrival = flight.scheduled_arrival + timedelta(minutes=delay_minutes)
                flight.delay_minutes = delay_minutes
                flight.is_delayed = 1
            else:
                flight.actual_departure = flight.scheduled_departure
                flight.actual_arrival = flight.scheduled_arrival
                flight.delay_minutes = 0
                flight.is_delayed = 0
                
        db.commit()
        
    finally:
        db.close()

if __name__ == "__main__":
    add_mock_delays()