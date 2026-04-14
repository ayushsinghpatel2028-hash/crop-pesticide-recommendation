import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier

df = pd.read_csv("data/Crop_recommendation_with_pesticide_enriched.csv")

df.columns = df.columns.str.strip()

print("Columns:", df.columns)

le_crop = LabelEncoder()
le_pest = LabelEncoder()

df['crop'] = le_crop.fit_transform(df['label'])
df['pesticide'] = le_pest.fit_transform(df['Pesticide'])

X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]

y_crop = df['crop']
y_pest = df['pesticide']

X_train, X_test, y_train, y_test = train_test_split(X, y_crop, test_size=0.2, random_state=42)


models = {
    "RandomForest": RandomForestClassifier(),
    "DecisionTree": DecisionTreeClassifier(),
    "SVM": SVC(),
    "KNN": KNeighborsClassifier(),
    "XGBoost": XGBClassifier()
}

accuracies = {}


for name, model in models.items():
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"{name} Accuracy: {acc}")

    accuracies[name] = acc

    joblib.dump(model, f"models/{name}.pkl")

joblib.dump(accuracies, "models/accuracies.pkl")

joblib.dump(le_crop, "models/le_crop.pkl")
joblib.dump(le_pest, "models/le_pest.pkl")

X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(X, y_pest, test_size=0.2, random_state=42)

pest_model = RandomForestClassifier()
pest_model.fit(X_train_p, y_train_p)

joblib.dump(pest_model, "models/pest_model.pkl")

print("✅ Training Completed Successfully!")