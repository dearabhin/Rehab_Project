# step1

Open VS Code, navigate to your project folder, and open an integrated terminal (Ctrl + ').

Create a virtual environment:

```
python -m venv rehab_env
```

Activate the environment:

```
.\rehab_env\Scripts\activate
```
Install the required libraries:

```
pip install pyserial scikit-learn joblib mediapipe opencv-python firebase-admin streamlit flask
```

# step2

The Python Backend (Data Processing & Inference)
The ESP32S code provided in the report's prints a specific string format to the Serial monitor . The Python script (main_inference.py) reads that serial port, uses regular expressions to extract the 9 features, loads your seniors' model.joblib file, makes a prediction, and pushes it to Firebase.

Note: Replace 'COM3' with the actual COM port your ESP32S is connected to, and ensure your model.joblib and Firebase JSON key are in the same directory.

# step3

The Streamlit Frontend (Dashboard)
To display the results to the doctor and patient, you will run a Streamlit app. This script (app.py) reads the live data from Firebase.

# step4

## How to Run the Demonstration:

To demonstrate this smoothly, you will need two terminals open in VS Code:

Terminal 1 (Backend): Make sure your virtual environment is active, the ESP32S is plugged in, and the model.joblib is ready. Run:
python main_inference.py

Terminal 2 (Frontend): In a separate terminal tab (also with the virtual environment active), run the Streamlit dashboard:
streamlit run app.py

This will automatically open the web dashboard in your browser. As the patient moves, the ESP32S sends data via serial, main_inference.py predicts the outcome using the Scikit-Learn model, pushes it to Firebase, and app.py updates the UI instantly.