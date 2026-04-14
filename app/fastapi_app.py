from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

models = {
    "RandomForest": joblib.load("models/RandomForest.pkl"),
    "DecisionTree": joblib.load("models/DecisionTree.pkl"),
    "SVM": joblib.load("models/SVM.pkl"),
    "KNN": joblib.load("models/KNN.pkl"),
    "XGBoost": joblib.load("models/XGBoost.pkl"),
}

pest_model = joblib.load("models/pest_model.pkl")
le_crop = joblib.load("models/le_crop.pkl")
le_pest = joblib.load("models/le_pest.pkl")

@app.post("/predict")
def predict(model_name: str, N: float, P: float, K: float, temp: float, humidity: float, ph: float, rainfall: float):

    model = models[model_name]

    data = np.array([[N, P, K, temp, humidity, ph, rainfall]])

    crop_pred = model.predict(data)
    pest_pred = pest_model.predict(data)

    crop = le_crop.inverse_transform(crop_pred)[0]
    pest = le_pest.inverse_transform(pest_pred)[0]

    return {
        "crop": crop,
        "pesticide": pest
    }