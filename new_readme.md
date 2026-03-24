This readme is for new app.py, which is for integrating Streamlit + MediaPipe + Firebase

How to run the complete setup:

Ensure your ESP32S is connected and the main_inference.py script (the one using Firebase) is running in your first terminal. This handles the serial data and ML model.

Run this updated app.py in your second terminal using ```streamlit run app.py```.

The web browser will pop up, showing the live MediaPipe skeletal tracking on the left, and your Firebase-synced hardware ML predictions on the right!