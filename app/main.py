from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Airport

app = FastAPI(title="Flight Delay Prediction System")

@app.get("/")
def root():
    return {"message": "Flight Delay Prediction API is running"}

@app.get("/airports")
def get_airports(db: Session = Depends(get_db)):
    airports = db.query(Airport).all()
    return airports

@app.get("/airports/{code}")
def get_airport(code: str, db: Session = Depends(get_db)):
    airport = db.query(Airport).filter_by(code=code).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport

@app.post("/airports")
def create_airport(code: str, name: str, city: str, country: str, db: Session = Depends(get_db)):
    existing = db.query(Airport).filter_by(code=code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Airport with this code already exists")
    new_airport = Airport(code=code, name=name, city=city, country=country)
    db.add(new_airport)
    db.commit()
    db.refresh(new_airport)
    return new_airport
