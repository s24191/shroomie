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
        conn.close()

        # Check if mushroom info was found
        if mushroom_info:
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
        # Clean up the uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                pass

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
