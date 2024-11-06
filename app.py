from flask import Flask, request, render_template, redirect, url_for
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.applications.efficientnet import preprocess_input
import numpy as np
import os

# Initialize the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Load the pre-trained model and EfficientNetB3 base model for feature extraction
model = load_model('shroomi_model.keras')
base_model = EfficientNetB3(include_top=False, weights='imagenet', pooling='avg')

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling image upload and prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Preprocess the image to fit the EfficientNetB3 input
    img = load_img(file_path, target_size=(300, 300))  # Resize image to the input size of the base model
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = preprocess_input(img_array)  # Preprocess for EfficientNet

    # Extract features using the base model
    features = base_model.predict(img_array)

    # Run the main model prediction
    predictions = model.predict(features)
    predicted_class = np.argmax(predictions, axis=1)[0]

    # Interpret the prediction
    # Update this list with all the possible classes from your training data
    class_names = ["Agaricus", "Amanita", "Boletus", "Cortinarius", "Entoloma", "Hygrocybe", "Lactarius", "Russula", "Suillus"]
    result = class_names[predicted_class]

    # Clean up: remove the saved file after prediction
    os.remove(file_path)

    return f"The mushroom is predicted to be: {result}"

if __name__ == '__main__':
    app.run(debug=True)
