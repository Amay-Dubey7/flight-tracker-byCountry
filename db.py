from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

# Define the base class for SQLAlchemy models
Base = declarative_base()

# Define the Flights table model
class Flight(Base):
    __tablename__ = 'flights'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    destination_airport = Column(String)
    src_airline_code = Column(String)
    src_country = Column(String)
    src_city = Column(String)
    src_identification_codeshare = Column(String)
    flight_number = Column(String)
    arrived_late = Column(String)
    estimated_late = Column(String)

def initialize_database():
    # Create a SQLite database engine
    engine = create_engine("sqlite:///flights.db")
    Base.metadata.create_all(engine)  # Create tables based on the models

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Check if data already exists
    existing_data = session.query(Flight).first()
    
    if existing_data is None:
        # Load the JSON data only if the database is empty
        DATA_FILE = "flight_data.json"
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            flight_data = json.load(f)

        # Insert the JSON data into the database
        for entry in flight_data:
            flight = Flight(
                destination_airport=entry.get("destination_airport"),
                src_airline_code=entry.get("src_airline_code"),
                src_country=entry.get("src_country"),
                src_city=entry.get("src_city"),
                src_identification_codeshare=entry.get("src_identification_codeshare"),
                flight_number=entry.get("flight_number"),
                arrived_late=entry.get("Arrived Late","0"),
                estimated_late=entry.get("Estimated Late","0")
            )
            session.add(flight)

        # Commit the session
        session.commit()
        print("Data successfully inserted into the database.")
    else:
        print("Database already contains data. Skipping insertion.")

    session.close()

if __name__ == "__main__":
    initialize_database()