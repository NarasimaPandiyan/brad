from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import joblib
import pandas as pd
import random

app = Flask(__name__)

# Specify the folder for storing models
MODELS_FOLDER = 'models'
app.config['MODELS_FOLDER'] = MODELS_FOLDER

# List of tips for hypertension
TIPS_FOR_HYPERTENSION = [
    "Maintain a healthy weight.",
    "Exercise regularly.",
    "Limit your alcohol intake.",
    "Reduce sodium (salt) in your diet.",
    "Quit smoking.",
    "Manage stress through relaxation techniques.",
    "Get enough quality sleep.",
    "Monitor your blood pressure regularly.",
    "Limit caffeine intake.",
    "Eat a healthy, balanced diet with plenty of fruits and vegetables.",
    "Avoid processed foods and excess sugar.",
    "Stay hydrated.",
    "Limit red meat and choose lean protein sources.",
    "Include foods rich in potassium in your diet.",
    "Consider reducing your intake of processed and packaged foods.",
    "Limit added sugars and sugary beverages.",
    "Use less added salt in your cooking.",
    "Engage in activities that bring you joy and relaxation.",
    "Consider mindfulness or meditation practices.",
    "Consult with a healthcare professional for personalized advice."
]

# Function to randomly select 2 or 3 tips
def get_random_tips():
    random.shuffle(TIPS_FOR_HYPERTENSION)
    return TIPS_FOR_HYPERTENSION[:3]

# Function to check if the file has an allowed extension
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']

    # If the user does not select a file, browser may also submit an empty part without a filename
    if file.filename == '':
        return redirect(request.url)

    # Check if the file has an allowed extension
    if file and allowed_file(file.filename):
        # Read the CSV file directly
        csv_data = pd.read_csv(file)

        # Load the saved model
        model_filename = 'gnb.joblib'  # Change this to your actual model filename
        model_path = os.path.join(app.config['MODELS_FOLDER'], model_filename)
        loaded_model = joblib.load(model_path)

        # Perform prediction
        predictions = loaded_model.predict(csv_data)

        # Get random tips for hypertension
        tips = get_random_tips()

        # Display the predictions and tips
        return render_template('prediction_result.html', predictions=predictions.tolist(), tips=tips)

    return 'Invalid file type. Allowed file type is: csv'

if __name__ == '__main__':
    # Create the 'models' folder if it doesn't exist
    if not os.path.exists(MODELS_FOLDER):
        os.makedirs(MODELS_FOLDER)

    app.run(debug=True)
