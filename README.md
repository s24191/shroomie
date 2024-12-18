# Shroomie

Shroomie is a web application that allows users to upload or capture images of mushrooms to predict their toxicity. The application also provides a history of previous predictions and allows users to filter the history based on mushroom names and dates.

## Features

- Capture or upload mushroom images for toxicity prediction.
- View prediction results in a modal.
- Maintain a history of predictions with details such as mushroom name, edibility, regions, and date.
- Filter history based on mushroom name and date.
- View locations of mushroom sightings on a map.
- User settings modal with logout functionality.

## Technologies Used

- Python
- JavaScript
- Flask
- Leaflet.js
- HTML/CSS

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/s24191/shroomie.git
    cd shroomie
    ```

2. Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask application:
    ```bash
    flask run
    ```

## Usage

1. Open the application in your web browser.
2. Capture or upload a mushroom image using the provided buttons.
3. View the prediction results in the modal.
4. Access the history of predictions and use the search bar to filter entries.
5. View the locations of mushroom sightings on the map.
6. Open the settings modal to log out or view user information.

## Project Structure

- `static/`: Contains static files such as CSS, JavaScript, and images.
- `templates/`: Contains HTML templates.
- `app.py`: Main Flask application file.
- `requirements.txt`: List of Python dependencies.

## Authors

- Yan Novikau
- Yehor Rafalovych
