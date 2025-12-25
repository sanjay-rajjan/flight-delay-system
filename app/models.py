from sqlalchemy import Column, Integer, String
from app.database import Base

class Airport(Base):
    __tablename__ = "airports"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    city = Column(String)
    country = Column(String)
