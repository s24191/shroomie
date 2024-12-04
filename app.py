import os
import base64
import sqlite3
import numpy as np
from flask import Flask, request, render_template, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.applications.efficientnet import preprocess_input

# Flask app initialization
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Load the pre-trained model
MODEL_PATH = 'shroomi_model.keras'
model = load_model(MODEL_PATH)

# Load EfficientNetB3 for feature extraction
base_model = EfficientNetB3(include_top=False, weights='imagenet', pooling='avg')

# Database configuration
DATABASE = 'Database/mushroom_database.db'

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Function to preprocess the image for the model
def preprocess_image(file_path):
    img = load_img(file_path, target_size=(300, 300))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array)

# Function to query the database for mushroom information
def fetch_mushroom_info(conn, mushroom_name):
    query = '''
        SELECT
            Mushroom.id AS mushroom_id,
            Mushroom.name AS mushroom_name,
            Mushroom.desc AS description,
            Mushroom.image AS image,
            Edible.name AS edibility,
            GROUP_CONCAT(Region.nam, ', ') AS regions
        FROM
            Mushroom
        LEFT JOIN
            Edible ON Mushroom.edible_id = Edible.id
        LEFT JOIN
            Mushroom_Region ON Mushroom.id = Mushroom_Region.Mushroom_id
        LEFT JOIN
            Region ON Mushroom_Region.Region_id = Region.id
        WHERE
            Mushroom.name = ?
        GROUP BY
            Mushroom.id
    '''
    return conn.execute(query, (mushroom_name,)).fetchone()

# Homepage route
@app.route('/')
def index():
    return render_template('index.html')

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    conn = None  # Initialize connection variable to None
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No selected file'}), 400

    # Handle latitude and longitude inputs
    latitude = request.form.get('latitude', None)
    longitude = request.form.get('longitude', None)

    # Save uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        # Preprocess image and make predictions
        img_array = preprocess_image(file_path)
        features = base_model.predict(img_array)
        predictions = model.predict(features)
        predicted_class_index = np.argmax(predictions, axis=1)[0]

        # Define class names
        class_names = ["Agaricus", "Amanita", "Boletus", "Cortinarius",
                       "Entoloma", "Hygrocybe", "Lactarius", "Russula", "Suillus"]
        predicted_mushroom_name = class_names[predicted_class_index]

        # Fetch mushroom info from the database
        conn = get_db_connection()
        mushroom_info = fetch_mushroom_info(conn, predicted_mushroom_name)

        if mushroom_info:
            # Convert database result to dictionary
            mushroom_info = dict(mushroom_info)

            # Convert the mushroom image from BLOB to base64
            image_blob: Optional[bytes] = mushroom_info.get('image')

            if image_blob:
                image_base64 = base64.b64encode(image_blob).decode('utf-8')
            else:
                image_base64 = None



    # Save history of the prediction
            user_image_blob = open(file_path, 'rb').read()

            conn.execute('''
                INSERT INTO History (User_id, Mushroom_id, user_image, date, latitude, longitude)
                VALUES (?, ?, ?, datetime('now'), ?, ?)
            ''', (1, mushroom_info['mushroom_id'], user_image_blob, latitude, longitude))
            conn.commit()

            # Prepare response
            result = {
                'name': mushroom_info['mushroom_name'],
                'description': mushroom_info['description'],
                'image': image_base64,
                'edibility': mushroom_info['edibility'],
                'regions': mushroom_info['regions']
            }
        else:
            result = {'error': 'Mushroom not found in the database'}

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Safely close the connection if it was successfully opened
        if conn is not None:
            conn.close()

        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify(result)

# History route
@app.route('/history', methods=['GET'])
def history():
    conn = get_db_connection()
    query = '''
        SELECT
            History.user_image,
            Mushroom.name AS mushroom_name,
            History.date,
            History.latitude,
            History.longitude
        FROM
            History
        JOIN
            Mushroom ON History.Mushroom_id = Mushroom.id
        ORDER BY
            History.date DESC
    '''
    history_entries = conn.execute(query).fetchall()
    conn.close()

    # Convert database results to a list of dictionaries
    history_list = []
    for entry in history_entries:
        user_image = entry['user_image']
        user_image_base64 = base64.b64encode(user_image).decode('utf-8') if user_image else None
        history_list.append({
            'user_image': user_image_base64,
            'mushroom_name': entry['mushroom_name'],
            'date': entry['date'],
            'latitude': entry['latitude'],
            'longitude': entry['longitude']
        })

    return jsonify(history_list)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
