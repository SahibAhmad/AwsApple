from tensorflow.keras.models import load_model
import numpy as np
from backend.utils import preprocess_image

model = load_model('backend/models/part_classifier.h5')

def classify_plant_part(image):
    # Preprocess image
    processed_img = preprocess_image(image)
    # Predict part type
    prediction = model.predict(processed_img)
    # Convert prediction to class label
    class_labels = ["leaf", "branch", "fruit", "other"]
    return class_labels[np.argmax(prediction)]
