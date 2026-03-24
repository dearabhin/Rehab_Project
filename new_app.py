# Abhin: Make sure you have mediapipe and opencv-python installed in your virtual environment.
# this new app.py is for Streamlit + MediaPipe + Firebase

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import cv2
import mediapipe as mp
import numpy as np

# 1. Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://your-project-id-default-rtdb.firebaseio.com/'
    })

ref = db.reference('rehabilitation_live_data')

# 2. Initialize MediaPipe Pose [cite: 1149-1150]
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Angle Calculation Function [cite: 1152-1167]
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

# 3. Streamlit Page Setup
st.set_page_config(page_title="Telehabilitation Portal", layout="wide")
st.title("AI-Based Post Knee Replacement Rehabilitation")

# Layout: Video on the left (wider), Metrics on the right
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Live Posture Analysis")
    video_placeholder = st.empty() # Placeholder for the video feed

with col2:
    st.header("Real-Time Sensor Metrics")
    feedback_placeholder = st.empty()
    metrics_placeholder = st.empty()

# 4. Video Capture and Real-Time Loop
# Initialize variables [cite: 1170-1171]
counter = 0
stage = None

# Start video capture [cite: 1173]
cap = cv2.VideoCapture(0)

# Start MediaPipe instance [cite: 1177]
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        # --- A. Fetch Data from Firebase ---
        data = ref.get()
        if data:
            prediction = data.get('prediction_class', -1)
            rms = data.get('emg_rms', 0.0)
            
            with feedback_placeholder.container():
                if prediction == 1:
                    st.success("Great job! EMG profile is correct.")
                elif prediction == 0:
                    st.error("Incorrect muscle activation. Adjust effort.")
                else:
                    st.info("Awaiting movement data...")
                    
            with metrics_placeholder.container():
                st.metric(label="Current Muscle Effort (RMS)", value=f"{rms:.2f}")

        # --- B. Process Webcam Feed with MediaPipe ---
        ret, frame = cap.read() [cite: 1179]
        if not ret:
            st.error("Failed to capture video.")
            break
        
        # Mirror image and convert colors for MediaPipe [cite: 1182-1185]
        frame = cv2.flip(frame, 1)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame [cite: 1187]
        results = pose.process(img_rgb)
        
        # Extract landmarks and draw [cite: 1189-1215]
        if results.pose_landmarks:
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates for Left Shoulder, Elbow, and Wrist [cite: 1194-1197]
                left_sh = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, 
                           landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                left_el = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, 
                           landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                left_wr = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, 
                           landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                
                # Calculate angle [cite: 1201]
                angle = calculate_angle(left_sh, left_el, left_wr)
                
                # Visualization of the angle [cite: 1210-1215]
                cv2.putText(img_rgb, str(int(angle)), 
                           tuple(np.multiply(left_el, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Bicep curl counting logic [cite: 1217-1223]
                if angle > 160:
                    stage = "down"
                if angle < 90 and stage == 'down':
                    stage = "up"
                    counter += 1
            except:
                pass
            
            # Draw landmarks on the RGB frame [cite: 1203-1209]
            mp_drawing.draw_landmarks(img_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
        # Overlay counter on the video feed [cite: 1224-1226]
        cv2.putText(img_rgb, f'REPS: {counter}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(img_rgb, f'STAGE: {stage}', (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

        # --- C. Push Video to Streamlit UI ---
        # We display the img_rgb frame directly in Streamlit
        video_placeholder.image(img_rgb, channels="RGB", use_column_width=True)

cap.release()