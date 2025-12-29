import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def train_model():
    df = pd.read_csv("flight_features.csv")
    feature_columns = [
        "hour", "day_of_week", "month", "is_weekend", "is_morning", "is_afternoon", "is_evening", "is_night",
        "dep_temperature", "dep_wind_speed", "dep_visibility", "dep_humidity", "airline_delay_rate", "route_delay_rate"]
    X = df[feature_columns]
    y = df["is_delayed"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy*100:.1f}%")

    with open("flight_delay_model.pkl", "wb") as file:
        pickle.dump(model, file)
    
    return model, accuracy

if __name__ == "__main__":
    model, accuracy = train_model()

