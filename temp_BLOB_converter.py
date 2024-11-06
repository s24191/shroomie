import sqlite3
import os

# Path to your SQLite database
DATABASE = 'mydb.db'  # Update with the correct path to your SQLite DB

# Convert image to binary (BLOB)
def convert_image_to_blob(image_path):
    with open(image_path, 'rb') as file:
        blob_data = file.read()
    return blob_data

# Function to update the Mushroom table with BLOB data
def update_mushroom_image(mushroom_id, image_blob):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Update the Mushroom table with the image BLOB
        cursor.execute("UPDATE Mushroom SET image = ? WHERE id = ?", (image_blob, mushroom_id))
        conn.commit()
        
        print(f"Image for Mushroom ID {mushroom_id} updated successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Main function to process all images in a directory
def process_images_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')):  # Add more extensions if needed
            # Assume filename is like "1.png", where 1 is the mushroom_id
            mushroom_id = int(os.path.splitext(filename)[0])
            image_path = os.path.join(directory_path, filename)
            
            # Convert image to BLOB and update the database
            image_blob = convert_image_to_blob(image_path)
            update_mushroom_image(mushroom_id, image_blob)

# Directory containing images
# File names should match mushroom IDs, e.g., "1.jpg" for mushroom ID 1
image_directory = 'uploads'  # Update this with the actual path

# Process the images
process_images_in_directory(image_directory)
