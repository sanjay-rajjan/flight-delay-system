## Flight Delay Prediction System

API that predicts flight delays with 85.7% accuracy by analyzing historical patterns, real time weather data, and airline performance metrics.

Flight delay predictions are made from multiple sources:
- Analyzes 1,000+ flight, airline, and airport data to identify delay patterns by airline and route
- Real time weather data from OpenWeatherMap API
- Considers departure time, day of week, and seasonal patterns

The Random Forest classifier model implemented for predictions is trained on 14 data features from these sources.

## Tech Stack

**Backend:**
- FastAPI
- PostgreSQL
- SQLAlchemy ORM

**Data & ML:**
- scikit-learn
- pandas

**External APIs:**
- AviationStack API
- OpenWeather API

**Tools:**
- Git
- Docker