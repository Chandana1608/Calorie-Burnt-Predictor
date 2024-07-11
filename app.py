from flask import Flask, render_template, request
import numpy as np
import joblib
import sqlite3

app = Flask(__name__)

# Load the pre-trained model
filename = 'calories_burnt.sav'
model = joblib.load(filename)

# Initialize SQLite database
def initialize_database():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")

    conn.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gender TEXT,
            age INTEGER,
            height REAL,
            weight REAL,
            duration REAL,
            heart_rate REAL,
            body_temp REAL,
            prediction REAL
        )
    ''')

    print("Table created successfully")
    conn.close()

# Function to initialize database at startup
initialize_database()

# Route to render index.html template
@app.route('/')
def index():
    # Provide gender options for the dropdown menu
    gender_options = ['Male', 'Female']
    return render_template('index.html', gender_options=gender_options)

# Route to handle prediction and store data in SQLite
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Retrieve form data
            gender = request.form['gender']
            age = int(request.form['age'])
            height = float(request.form['height'])
            weight = float(request.form['weight'])
            duration = float(request.form['duration'])
            heartRate = float(request.form['heartRate'])
            bodyTemp = float(request.form['bodyTemp'])

            # Convert gender to numerical value (assuming 'male' = 0, 'female' = 1 for example)
            gender_code = 0 if gender.lower() == 'male' else 1

            # Prepare input data for prediction
            input_data = np.array([[gender_code, age, height, weight, duration, heartRate, bodyTemp]])

            # Make prediction
            prediction = model.predict(input_data)[0]
            prediction = round(prediction, 2)
            print(f"Predicted Calories Burnt: {prediction}") 

            # Store prediction and input data in database
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Ensure prediction is stored as float in SQLite
            cursor.execute('''
                INSERT INTO predictions (gender, age, height, weight, duration, heart_rate, body_temp, prediction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (gender, age, height, weight, duration, heartRate, bodyTemp, float(prediction)))
            
            conn.commit()
            conn.close()

            return render_template('index.html', prediction_text=f'Calories Burnt: {prediction}', gender_options=['Male', 'Female'])
        except Exception as e:
            return str(e)

# Route to display historical predictions
@app.route('/history')
def history():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM predictions ORDER BY id DESC') # Order by id in descending order
        data = cursor.fetchall()
        conn.close()
        return render_template('history.html', predictions=data)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
