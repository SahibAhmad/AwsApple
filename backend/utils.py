from flask import Flask, request, jsonify
import tensorflow as tf
from PIL import Image
import numpy as np
app = Flask(__name__)
model = tf.keras.models.load_model('../model-train/classifier.h5')
@app.route('/classify_part', methods=['POST'])
def classify_part():
    image = request.files.get('image')
    if not image:
        return jsonify({"error": "No image provided"}), 400
    try:
        img = Image.open(image)
        img = img.resize((224, 224))  
        img = np.array(img) / 255.0  
        img = np.expand_dims(img, axis=0)  
    except Exception as e:
        return jsonify({"error": f"Error processing image: {e}"}), 400
    try:
        predictions = model.predict(img)
        class_names = ['alternaria', 'healthy', 'insect', 'mlb', 'mosaic', 'multiple', 'necrosis', 'powdery-mildew', 'scab']
        predicted_class = class_names[np.argmax(predictions)]
        return jsonify({'part_type': predicted_class})
    except Exception as e:
        return jsonify({"error": f"Error during model prediction: {e}"}), 500
if __name__ == '__main__':
    app.run(debug=True)
