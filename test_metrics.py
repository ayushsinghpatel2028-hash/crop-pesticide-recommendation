import joblib

class_metrics = joblib.load("models/class_metrics.pkl")
le_crop = joblib.load("models/le_crop.pkl")

print("Keys of class_metrics:", class_metrics.keys())
rf_metrics = class_metrics["RandomForest"]
print("Keys of rf_metrics:", list(rf_metrics.keys())[:5])
print("Sample class metric:", rf_metrics[list(rf_metrics.keys())[0]])
print("le_crop classes:", le_crop.classes_[:5])
