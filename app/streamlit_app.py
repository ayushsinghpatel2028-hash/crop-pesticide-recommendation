import streamlit as st
import requests
import joblib
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="Crop AI System", layout="wide", page_icon="🌾")

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Global background and fonts */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #f1f2f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #A8E063, #56AB2F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    h2, h3 {
        color: #A8E063;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    /* Input widgets styling */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #56AB2F 0%, #A8E063 100%);
        color: #000;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        border: none;
        padding: 0.6rem;
        box-shadow: 0 4px 15px rgba(86, 171, 47, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(86, 171, 47, 0.6);
        color: #000;
        border: none;
    }
    
    /* Horizontal rule */
    hr {
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0));
        margin: 2rem 0;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #A8E063;
    }
</style>
""", unsafe_allow_html=True)


st.title("🌾 AI Crop & Pesticide Recommendation System")
st.write("<h4 style='text-align: center; color: #E0E0E0; font-weight: 400;'>Smart Agriculture powered by Advanced Machine Learning 🚜</h4>", unsafe_allow_html=True)
st.markdown("---")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

farm_path = os.path.join(BASE_DIR, "..", "assets", "farm.jpg")
crop_path = os.path.join(BASE_DIR, "..", "assets", "crop.jpg")
pest_path = os.path.join(BASE_DIR, "..", "assets", "pesticides.jpg")

col1, col2, col3 = st.columns(3)

with col1:
    if os.path.exists(farm_path):
        st.image(farm_path, use_container_width=True, caption="Smart Farming")
    else:
        st.warning("farm.jpg not found")

with col2:
    if os.path.exists(crop_path):
        st.image(crop_path, use_container_width=True, caption="Crop Yields")
    else:
        st.warning("crop.jpg not found")

with col3:
    if os.path.exists(pest_path):
        st.image(pest_path, use_container_width=True, caption="Pest Control")
    else:
        st.warning("pesticides.jpg not found")

st.markdown("---")

st.subheader("🧪 Step 1: Enter Soil & Weather Details")
st.write("Provide the latest environmental readings for accurate recommendations.")

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        N = st.number_input("Nitrogen (N)", 0, 150, 50, help="Nitrogen content in soil")
        P = st.number_input("Phosphorus (P)", 0, 150, 50, help="Phosphorus content in soil")

    with col2:
        K = st.number_input("Potassium (K)", 0, 150, 50, help="Potassium content in soil")
        temp = st.slider("Temperature (°C)", 0, 50, 25, help="Current temperature")

    with col3:
        humidity = st.slider("Humidity (%)", 0, 100, 60, help="Relative humidity")
        ph = st.slider("pH Level", 0.0, 14.0, 6.5, help="Soil pH level")
        rainfall = st.slider("Rainfall (mm)", 0, 300, 100, help="Average rainfall")

st.markdown("<br>", unsafe_allow_html=True)

st.subheader("🤖 Step 2: Select Predictive Engine")
col1, col2 = st.columns([1, 2])
with col1:
    model_choice = st.selectbox(
        "Choose a trained Machine Learning Model:",
        ["RandomForest", "DecisionTree", "SVM", "KNN", "XGBoost"]
    )
    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("🚀 Run Prediction Analysis")

with col2:
    if predict_btn:
        try:
            with st.spinner('Analyzing data and running models...'):
                res = requests.post(
                    "http://127.0.0.1:8000/predict",
                    params={
                        "model_name": model_choice,
                        "N": N, "P": P, "K": K,
                        "temp": temp, "humidity": humidity,
                        "ph": ph, "rainfall": rainfall
                    }
                )
            if res.status_code == 200:
                data = res.json()
                st.success(f"### 🌱 Recommended Crop: **{data['crop'].upper()}**")
                st.info(f"### 🧪 Recommended Pesticide: **{data['pesticide']}**")
            else:
                st.error("Error from prediction server.")
        except Exception as e:
            st.error("❌ FastAPI server not running! Please run `uvicorn app.fastapi_app:app --reload` first.")

st.markdown("---")

st.subheader("📊 Model Performance & Insights")

try:
    acc = joblib.load("models/accuracies.pkl")
    class_metrics = joblib.load("models/class_metrics.pkl")
    le_crop = joblib.load("models/le_crop.pkl")
    
    tab1, tab2 = st.tabs(["🏆 Overall Accuracy", "🎯 Class-Wise Comparison"])
    
    with tab1:
        st.write("Compare the overall accuracy of the different machine learning models trained on the dataset.")
        df_acc = pd.DataFrame(list(acc.items()), columns=["Model", "Accuracy"])
        df_acc = df_acc.sort_values(by="Accuracy", ascending=False)
        
        # Plotly overall accuracy
        fig_acc = px.bar(
            df_acc, x="Model", y="Accuracy",
            color="Accuracy",
            color_continuous_scale="Viridis",
            text_auto='.3f',
            title="Overall Model Accuracy Comparison"
        )
        fig_acc.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=20
        )
        st.plotly_chart(fig_acc, use_container_width=True)
        
    with tab2:
        st.write("Deep dive into the metrics for each specific crop across the different models.")
        
        # Prepare data for class-wise comparison
        records = []
        # Class names from label encoder
        class_names = le_crop.classes_
        
        for model_name, metrics in class_metrics.items():
            for class_idx_str, class_metrics_data in metrics.items():
                if class_idx_str.isdigit():  # ignore 'accuracy', 'macro avg', etc.
                    class_id = int(class_idx_str)
                    crop_name = class_names[class_id]
                    records.append({
                        "Model": model_name,
                        "Crop": crop_name,
                        "F1-Score": class_metrics_data["f1-score"],
                        "Precision": class_metrics_data["precision"],
                        "Recall": class_metrics_data["recall"]
                    })
        
        df_class = pd.DataFrame(records)
        
        # Choose metric to display
        metric_choice = st.radio("Select Metric to Visualize:", ["F1-Score", "Precision", "Recall"], horizontal=True)
        
        # Plotly grouped bar chart for class-wise comparison
        fig_class = px.bar(
            df_class, 
            x="Crop", 
            y=metric_choice, 
            color="Model", 
            barmode="group",
            title=f"Crop-Wise {metric_choice} by Model",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_class.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_title="Crop Type",
            yaxis_title=metric_choice,
            legend_title="Algorithm",
            height=600
        )
        st.plotly_chart(fig_class, use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Could not load models or metrics. Train models first to see graphs. Error: {e}")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>👨‍💻 Developed by Ayush Singh 🚀</p>", unsafe_allow_html=True)