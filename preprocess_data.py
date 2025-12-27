# preprocess_data.py
# Usage: python preprocess_data.py
# - Loads cars_data.csv
# - Encodes categorical variables
# - Trains a RandomForestClassifier to predict `brand`
# - Saves a model and encoders to disk (car_brand_model.pkl)

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[0] / "cars_data.csv"
MODEL_PATH = Path(__file__).resolve().parents[0] / "car_brand_model.pkl"

def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    return df

def train_and_save():
    df = load_data()

    print("\n=== Original Data (Before Preprocessing) ===")
    print(df.head())  # Display first 5 rows of original data
    print("\nData info:")
    print(df.info())

    X = df.drop(columns=["brand"])
    y = df["brand"]

    # Simple preprocessing: label encode categorical features and the target
    encoders = {}
    X_enc = X.copy()
    for col in ["fuel_type", "transmission"]:
        le = LabelEncoder()
        X_enc[col] = le.fit_transform(X_enc[col].astype(str))
        encoders[col] = le

    y_le = LabelEncoder()
    y_enc = y_le.fit_transform(y)
    encoders["brand"] = y_le

    print("\n=== Encoded Data (After Preprocessing) ===")
    print(X_enc.head())
    print("\nEncoded target sample:", y_enc[:10])

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_enc, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X_train, y_train)

    print("\n=== Model Performance ===")
    print("Train accuracy: {:.3f}".format(model.score(X_train, y_train)))
    print("Test accuracy: {:.3f}".format(model.score(X_test, y_test)))

    joblib.dump({"model": model, "encoders": encoders}, MODEL_PATH)
    print("\nSaved model + encoders to", MODEL_PATH)

if __name__ == "__main__":
    train_and_save()
