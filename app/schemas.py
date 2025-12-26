from pydantic import BaseModel

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