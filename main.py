from flask import Flask, render_template, request, redirect, jsonify, url_for
import os
import joblib
import pandas as pd
import json
import random
import uuid  # Import the uuid module for generating unique IDs

app = Flask(__name__)

# Specify the folder for storing models and results
MODELS_FOLDER = 'models'
RESULTS_FOLDER = 'results'
app.config['MODELS_FOLDER'] = MODELS_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

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

# Function to write results and tips to a JSON file
# Function to write results and tips to a JSON file
def write_results_to_json(results):


    # Convert NumPy int64 types to standard Python int
    for result in results:
        result['Age'] = int(result['Age'])

    result_id = 1  # Generate a unique ID for the result set  
    for row in results:
        
        result_filename = f'result_{result_id}.json'
        result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
        result_data = {
            'results': row,
            'tips': get_random_tips()
        }

        with open(result_path, 'w+') as json_file:
            json.dump(result_data, json_file, default=str)  # Use default=str to handle other non-serializable types
        result_id+=1
        

@app.route('/')
def index():
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']

    # If the user does not select a file, the browser may also submit an empty part without a filename
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

        # Create a list to store results for each row
        results = []

        for _, row in csv_data.iterrows():
            # Extract relevant features
            age = row['Age']
            sex = row['Sexe']
            height = row['Height']
            weight = row['Weight']

            # Calculate BMI
            bmi = weight / ((height / 100) ** 2)

            # Perform prediction
            prediction = loaded_model.predict([row])[0]

            # Create a dictionary for each row's result
            result_dict = {
                'Age': age,
                'Sex': sex,
                'Height': height,
                'Weight': weight,
                'BMI': bmi,
                'Prediction': prediction
            }

            # Append the dictionary to the results list
            results.append(result_dict)

        # Write results and tips to a JSON file, get the unique ID
        print(results)
        write_results_to_json(results)

        # Redirect to the result page with the unique ID
        return redirect(url_for('result_page', result_id=1))

    return 'Invalid file type. Allowed file type is: csv'

@app.route('/result/<result_id>')
def result_page(result_id):
    # Load results and tips from the JSON file based on the provided ID
    result_filename = f'result_{result_id}.json'
    result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)

    try:
        with open(result_path, 'r') as json_file:
            result_data = json.load(json_file)
    except FileNotFoundError:
        return 'Result not found.'

    return render_template('result_page.html', results=result_data['results'], tips=result_data['tips'])

if __name__ == '__main__':
    # Create the 'models' and 'results' folders if they don't exist
    for folder in [MODELS_FOLDER, RESULTS_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    app.run(debug=True)
