import streamlit as st
import requests
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Crop AI System", layout="wide")


st.title("🌾 AI Crop & Pesticide Recommendation System")
st.write("Smart Agriculture using Machine Learning 🚜")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

farm_path = os.path.join(BASE_DIR, "..", "assets", "farm.jpg")
crop_path = os.path.join(BASE_DIR, "..", "assets", "crop.jpg")
pest_path = os.path.join(BASE_DIR, "..", "assets", "pesticides.jpg")

col1, col2, col3 = st.columns(3)

with col1:
    if os.path.exists(farm_path):
        st.image(farm_path, use_container_width=True)
    else:
        st.warning("farm.jpg not found")

with col2:
    if os.path.exists(crop_path):
        st.image(crop_path, use_container_width=True)
    else:
        st.warning("crop.jpg not found")

with col3:
    if os.path.exists(pest_path):
        st.image(pest_path, use_container_width=True)
    else:
        st.warning("pesticides.jpg not found")


st.markdown("---")
st.subheader("🧪 Enter Soil & Weather Details")

col1, col2, col3 = st.columns(3)

with col1:
    N = st.number_input("Nitrogen (N)", 0, 150, 50)
    P = st.number_input("Phosphorus (P)", 0, 150, 50)

with col2:
    K = st.number_input("Potassium (K)", 0, 150, 50)
    temp = st.slider("Temperature (°C)", 0, 50, 25)

with col3:
    humidity = st.slider("Humidity (%)", 0, 100, 60)
    ph = st.slider("pH Level", 0.0, 14.0, 6.5)
    rainfall = st.slider("Rainfall (mm)", 0, 300, 100)


model_choice = st.selectbox(
    "🤖 Select Machine Learning Model",
    ["RandomForest", "DecisionTree", "SVM", "KNN", "XGBoost"]
)

st.markdown("---")

if st.button("🚀 Predict Now"):

    try:
        res = requests.post(
            "http://127.0.0.1:8000/predict",
            params={
                "model_name": model_choice,
                "N": N,
                "P": P,
                "K": K,
                "temp": temp,
                "humidity": humidity,
                "ph": ph,
                "rainfall": rainfall
            }
        )

        data = res.json()

        st.success(f"🌱 Recommended Crop: {data['crop']}")
        st.info(f"🧪 Recommended Pesticide: {data['pesticide']}")

    except:
        st.error("❌ FastAPI server not running! Run FastAPI first.")


st.markdown("---")
st.subheader("📊 Model Accuracy Comparison")

try:
    acc = joblib.load("models/accuracies.pkl")
    df = pd.DataFrame(list(acc.items()), columns=["Model", "Accuracy"])

    fig, ax = plt.subplots()
    ax.bar(df["Model"], df["Accuracy"])
    ax.set_title("Model Accuracy")
    ax.set_xlabel("Models")
    ax.set_ylabel("Accuracy")

    st.pyplot(fig)

except:
    st.warning("⚠️ Train models first to see accuracy graph")


st.markdown("---")
st.write("👨‍💻 Developed by Ayush Singh 🚀")