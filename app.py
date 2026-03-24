import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# Initialize Firebase (Ensure this runs only once)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://your-project-id-default-rtdb.firebaseio.com/'
    })

ref = db.reference('rehabilitation_live_data')

st.set_page_config(page_title="Telehabilitation Portal", layout="wide")
st.title("AI-Based Post Knee Replacement Rehabilitation")

# Dashboard Layout
col1, col2 = st.columns(2)

with col1:
    st.header("Patient Dashboard")
    st.write("Live Exercise Feedback")
    feedback_placeholder = st.empty()

with col2:
    st.header("Doctor Dashboard")
    st.write("Live Sensor Metrics")
    metrics_placeholder = st.empty()

# Real-time update loop
while True:
    data = ref.get()
    
    if data:
        prediction = data.get('prediction_class', -1)
        rms = data.get('emg_rms', 0.0)
        
        with feedback_placeholder.container():
            if prediction == 1:
                st.success("Great job! Posture is correct.")
            elif prediction == 0:
                st.error("Incorrect posture. Please adjust your knee angle.")
            else:
                st.info("Awaiting movement...")
                
        with metrics_placeholder.container():
            st.metric(label="Current Muscle Effort (RMS)", value=f"{rms:.2f}")
            
    time.sleep(1) # Refresh rate