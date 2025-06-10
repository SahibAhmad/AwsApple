from tensorflow.keras.models import load_model
import numpy as np
from backend.utils import preprocess_image

model = load_model('backend/models/disease_detector.h5')

def detect_disease(image):
    # Preprocess image
    processed_img = preprocess_image(image)
    # Predict disease
    prediction = model.predict(processed_img)
    # Convert prediction to class label
    disease_labels = ["healthy", "disease_1", "disease_2", ...]  # Add remaining disease labels
    return disease_labels[np.argmax(prediction)]
