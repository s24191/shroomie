#%%
import numpy as np
import os
import shutil
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import seaborn as sns
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from collections import Counter
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import MiniBatchKMeans
from imblearn.under_sampling import ClusterCentroids
from imblearn.under_sampling import NearMiss
from imblearn.over_sampling import RandomOverSampler


#%%
base_model = EfficientNetB3(include_top=False, weights='imagenet', pooling='avg')

ros = RandomOverSampler(random_state=42)

writable_directory = 'working/Mushrooms'
validation_directory = 'working/validation'
training_directory = 'working/training'
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def count_images(directory):
    class_counts = {}
    for class_name in os.listdir(directory):
        class_directory = os.path.join(directory, class_name)
        if os.path.isdir(class_directory):
            class_counts[class_name] = len(os.listdir(class_directory))
    return class_counts

def load_and_process_image(image_path, target_size=(300, 300)):
    img = load_img(image_path, target_size=target_size)
    img_array = img_to_array(img)
    return img_array.flatten()  # Convert to 1D array

print("Class counts before oversampling:")
class_counts_before = count_images(writable_directory)
for class_name, count in class_counts_before.items():
    print(f"{class_name}: {count}")
    
    
#%%
# Oversampling
class_counts = class_counts_before
max_count = max(class_counts.values())

X = []
y = []
for class_name, count in class_counts.items():
    class_directory = os.path.join(writable_directory, class_name)
    images = os.listdir(class_directory)

    # Load and process images into numeric arrays


    for image in images:
        image_path = os.path.join(class_directory, image)
        img = load_img(image_path, target_size=(300, 300))
        img_array = img_to_array(img)
        
        X.append(img_array)
        y.append(class_name)

X = np.array(X)
X = base_model.predict(X.reshape(X.shape[0], 300, 300, 3), verbose=0)  # Extract features
y = np.array(y)

# Flatten X to 2D array
num_samples, img_size = X.shape[0], np.prod(X.shape[1:])
X = X.reshape(num_samples, img_size)

# Fit SMOTE on the current class
X_resampled, y_resampled = ros.fit_resample(X, y)
print(X_resampled.shape)

input_shape = (300, 300, 3)  
num_classes = len(class_counts_before)  
batch_size = 64  
X_train1, X_test1, y_train1, y_test1 = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42)

# %%
from sklearn.preprocessing import LabelEncoder
import keras

X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42)
le = LabelEncoder()
y = le.fit_transform(y_train)
y = keras.utils.to_categorical(y, num_classes=9)

y_test = le.fit_transform(y_test)
y_test = keras.utils.to_categorical(y_test, num_classes=9)

#%%
le = LabelEncoder()
y1 = le.fit_transform(y_train1)
y1 = keras.utils.to_categorical(y1, num_classes=9)

y_test1 = le.fit_transform(y_test1)
y_test1 = keras.utils.to_categorical(y_test1, num_classes=9)

#%%
print(X_resampled.shape)
input_shape = (1536,)
inputs = tf.keras.Input(shape=input_shape)


x = tf.keras.layers.Dense(1024, activation='relu')(inputs)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
model = tf.keras.Model(inputs, outputs)


model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

history_fine = model.fit(
    x=X_train,
    y=y,
    epochs=10,  
)

val_loss, val_accuracy = model.evaluate(X_test1, y_test1)
print(f"Validation Accuracy: {val_accuracy}")
predictions = model.predict(X_test1)

predicted_classes = np.argmax(predictions, axis=1)
true_classes = np.argmax(y_test1, axis=1)

print(classification_report(true_classes, predicted_classes))
cm = confusion_matrix(true_classes, predicted_classes)

plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()

#%%
model.save('shroomi_model.keras')


#%%
# Example URLs of images to test
image_urls = [
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT1uLNRFhaxJNr5Tyx3Phok3oVMehO369GrXg&s",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Agaricus_augustus_2011_G1.jpg/1200px-Agaricus_augustus_2011_G1.jpg",
    "https://ultimate-mushroom.com/images/agaricus-sylvicola-1.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjgTAXUN8gHfl9Uov6WAlD2AxP3mzSK4CufA&s",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Amanita_muscaria_3_vliegenzwammen_op_rij.jpg/800px-Amanita_muscaria_3_vliegenzwammen_op_rij.jpg",
    "https://ultimate-mushroom.com/images/lactarius-subdulcis-2.jpg",
    "https://ultimate-mushroom.com/images/lactarius-semisanguifluus-1.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhyYlG10YgM4iVuvUQsUwlNJ3jchyOudO91Q&s",
    "https://grzyby-pk.pl/gat-l/imgduze/lactarius-trivialis.jpg",
]

import requests
from io import BytesIO

# Load and preprocess image from URL
def load_image_from_url(url, target_size=(300, 300)):
    response = requests.get(url)
    img = load_img(BytesIO(response.content), target_size=target_size)
    img_array = img_to_array(img)
    img_array = img_array.reshape((1, *target_size, 3))  # Reshape for model input
    return img_array

# Predict on images from URLs
def predict_on_images(image_urls, model, le):
    for url in image_urls:
        img_array = load_image_from_url(url)
        img_features = base_model.predict(img_array)  # Extract features using base model
        prediction = model.predict(img_features)
        predicted_class = le.inverse_transform([np.argmax(prediction)])
        
        print(f"Image URL: {url}")
        print(f"Predicted Class: {predicted_class[0]}")

# Run predictions
predict_on_images(image_urls, model, le)

# %%
