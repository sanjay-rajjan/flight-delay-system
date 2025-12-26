from app.database import Base, engine
from app.models import Airport, Airline, Flight

def create_tables():
    print("Creating database tables")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")


if __name__ == "__main__":
    create_tables()

