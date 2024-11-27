import sqlite3
from flask import Flask, request, render_template, redirect, url_for, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.applications.efficientnet import preprocess_input
import numpy as np
import os
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Load the model and base model for feature extraction
model = load_model('shroomi_model.keras')
base_model = EfficientNetB3(include_top=False, weights='imagenet', pooling='avg')

# Database path
DATABASE = 'mushroom_database.db'

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling image upload and prediction
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Handle latitude and longitude gracefully
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    if not latitude or not longitude:
        latitude = None  # Set to None if not provided
        longitude = None  # Set to None if not provided

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        # Preprocess the image for EfficientNetB3
        img = load_img(file_path, target_size=(300, 300))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Extract features
        features = base_model.predict(img_array)
        predictions = model.predict(features)
        predicted_class_index = np.argmax(predictions, axis=1)[0]

        # Replace with the actual class names used in your model
        class_names = ["Agaricus", "Amanita", "Boletus", "Cortinarius", "Entoloma", "Hygrocybe", "Lactarius", "Russula", "Suillus"]
        predicted_mushroom_name = class_names[predicted_class_index]

        # Query the database for the predicted mushroom info including region and edibility
        conn = get_db_connection()
        mushroom_info = conn.execute('''
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
        ''', (predicted_mushroom_name,)).fetchone()

        if mushroom_info:
            # Convert user-uploaded image to BLOB for storage
            with open(file_path, 'rb') as f:
                user_image_blob = f.read()

            # Save the history
            user_id = 1  # Replace with the actual user ID (e.g., from authentication)
            conn.execute('''
                INSERT INTO History (User_id, Mushroom_id, user_image, date, latitude, longitude)
                VALUES (?, ?, ?, datetime('now'), ?, ?)
            ''', (user_id, mushroom_info['mushroom_id'], user_image_blob, latitude, longitude))
            conn.commit()

            # Prepare the response
            image_blob = mushroom_info['image']
            if image_blob is not None:
                image_base64 = base64.b64encode(image_blob).decode('utf-8')
            else:
                image_base64 = None

            result = {
                'name': mushroom_info['mushroom_name'],
                'description': mushroom_info['description'],
                'image': image_base64,
                'edibility': mushroom_info['edibility'],
                'regions': mushroom_info['regions']
            }
        else:
            result = {'error': 'Mushroom not found in the database'}

    finally:
        conn.close()

        # Clean up the uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                pass

    return jsonify(result)

@app.route('/history', methods=['GET'])
def history():
    conn = get_db_connection()
    history_entries = conn.execute('''
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
    ''').fetchall()
    conn.close()

    history_list = []
    for entry in history_entries:
        user_image = entry['user_image']
        if user_image is not None:
            user_image = base64.b64encode(user_image).decode('utf-8')
        history_list.append({
            'user_image': user_image,
            'mushroom_name': entry['mushroom_name'],
            'date': entry['date'],
            'latitude': entry['latitude'],
            'longitude': entry['longitude']
        })

    return jsonify(history_list)

if __name__ == '__main__':
    app.run(debug=True)
