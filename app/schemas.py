from pydantic import BaseModel
from datetime import datetime

class AirportBase(BaseModel):
    code: str
    name: str
    city: str
    country: str

class AirportCreate(AirportBase):
    pass

class Airport(AirportBase):
    id: int
    class Config:
        from_attributes = True

class AirlineBase(BaseModel):
    code: str
    name: str

class AirlineCreate(AirlineBase):
    pass

class Airline(AirlineBase):
    id: int
    class Config:
        from_attributes = True

class FlightBase(BaseModel):
    flight_number: str
    airline_id: int
    departure_airport_id: int
    arrival_airport_id: int
    scheduled_departure: datetime
    scheduled_arrival: datetime

class FlightCreate(FlightBase):
    pass

class Flight(FlightBase):
    id: int
    airline: Airline
    departure_airport: Airport
    arrival_airport: Airport

    class Config:
        from_attributes = True