## Flight Delay Prediction System

API that predicts flight delays with 86% accuracy by analyzing historical patterns, real time weather data, and airline performance metrics.

Flight delay predictions are made from multiple sources:
- Analyzes 3,400+ real historical flights from a published dataset to identify delay patterns by airline and route
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
- Kaggle Flight Delay Dataset
- OpenWeather API

**Tools:**
- Git
- Docker