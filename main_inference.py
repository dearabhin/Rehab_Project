import serial
import re
import joblib
import firebase_admin
from firebase_admin import credentials, db
import time

# 1. Initialize Firebase (Replace with your actual Firebase project details)
# You need to download the serviceAccountKey.json from your Firebase Console
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project-id-default-rtdb.firebaseio.com/'
})
ref = db.reference('rehabilitation_live_data')

# 2. Load the Scikit-Learn Model
try:
    model = joblib.load('model.joblib')
    print("ML Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")

# 3. Setup Serial Connection to ESP32S
# Change 'COM3' to your ESP32S COM port (check Arduino IDE or Device Manager)
SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to ESP32S on {SERIAL_PORT}")
except Exception as e:
    print(f"Failed to connect to serial: {e}")
    exit()

def parse_esp32_data(line):
    """
    Extracts the 9 numerical features from the ESP32 print statement.
    Expected format from Appendix:
    EMG RMS: 12.3 EMG MAV: 10.1 EMG WL: 45.2 Gyro Peak: [1.2, 0.5, 0.1] Gyro ROM (deg): [10.1, 5.2, 2.1]
    """
    try:
        # Extract all floating point numbers from the string
        numbers = re.findall(r"[-+]?(?:\d*\.*\d+)", line)
        if len(numbers) >= 9:
            # Order: RMS, MAV, WL, PeakX, PeakY, PeakZ, ROMx, ROMy, ROMz
            features = [float(x) for x in numbers[:9]]
            return features
    except Exception as e:
        pass
    return None

print("Listening for sensor data...")

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        
        # Parse the string into an array of 9 features
        features = parse_esp32_data(line)
        
        if features:
            # 4. Run ML Inference
            # The model expects a 2D array: [[f1, f2, ... f9]]
            prediction = model.predict([features])[0]
            
            print(f"Features: {features} | Prediction: {prediction}")
            
            # 5. Push Data to Firebase [cite: 537]
            data_to_upload = {
                'timestamp': time.time(),
                'emg_rms': features[0],
                'prediction_class': int(prediction) # Adjust depending on your model's output
            }
            ref.set(data_to_upload)