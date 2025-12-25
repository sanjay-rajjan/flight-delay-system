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