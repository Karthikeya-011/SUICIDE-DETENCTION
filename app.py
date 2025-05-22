from flask import Flask, request, jsonify, render_template
import smtplib
import os
import numpy as np
import pickle
from dotenv import load_dotenv
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import mysql.connector
from mysql.connector import Error

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Load model and tokenizer
model = load_model('Twitter_Suicidal_Ideation_Detection_GRU.h5', compile=False)
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Database connection helper
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'your_mysql_user'),
        password=os.getenv('DB_PASSWORD', 'your_mysql_password'),
        database=os.getenv('DB_NAME', 'suicide_monitoring')
    )

# Routes for HTML pages
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/resources.html')
def resources():
    return render_template('resources.html')

# Suicide ideation prediction API
@app.route('/suicide-ideation', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '').strip()

    if not text:
        return jsonify({
            'predictionText': 'Please enter some text.',
            'prediction': 0.0
        })

    sequence = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(sequence, maxlen=60, dtype='int32')
    predicted = model.predict(padded, batch_size=1, verbose=False)

    label_index = int(np.argmax(predicted))
    prediction_score = float(predicted[0][label_index])

    if label_index == 0:
        predictionText = "Potential Suicide Post"
    elif label_index == 1:
        predictionText = "Non Suicide Post"
    else:
        predictionText = "Unknown"

    # Save to DB
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO prediction_logs (input_text, predicted_label, confidence_score) VALUES (%s, %s, %s)"
        cursor.execute(sql, (text, predictionText, prediction_score))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error while saving to DB: {e}")

    return jsonify({
        'predictionText': predictionText,
        'prediction': prediction_score
    })

# Contact form handler
@app.route('/send-email', methods=['POST'])
def send_email():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    subject = f'Contact Form Submission from {name}'
    body = f'Name: {name}\nEmail: {email}\nMessage: {message}'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
    server.sendmail(os.getenv('EMAIL_USER'), 'karthikeyak54321@gmail.com', subject + '\n\n' + body)
    server.quit()

    return render_template('thank-you.html')

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
