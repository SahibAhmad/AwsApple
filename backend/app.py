from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from PIL import Image
from db import get_all_products, user_exists, get_user_info ,get_all_products,add_user
import numpy as np
from Data import data
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)
part_classifier_model = tf.keras.models.load_model('../model-train/classifier.h5')
disease_detection_model = tf.keras.models.load_model('../model-train/apple_disease_detector.h5')
part_classes = ['leaf', 'non-leaf']
disease_classes = [
    'alternaria', 'healthy',  'mossaic', 'scab'
]
def preprocess_image(image, target_size=(224, 224)):
    image = Image.open(image)
    image = image.convert('RGB')
    image = image.resize(target_size)
    image = np.array(image)
    image = preprocess_input(image)
    image = np.expand_dims(image, axis=0)
    return image
def classify_plant_part(image):
    processed_image = preprocess_image(image)
    predictions = part_classifier_model.predict(processed_image)
    if (predictions > 0.5):
        return "non-leaf";
    else:
        return "leaf"
def detect_disease(image):
    processed_image = preprocess_image(image)
    predictions = disease_detection_model.predict(processed_image)
    return disease_classes[np.argmax(predictions)]
def get_chemicals(disease=None):
    # Random stage selection (as in the original function)
    stage = "Fruit development"
    # Match disease with chemical recommendations
    for stage_info in data["spray_schedule"]:
        if stage_info["stage"].lower() == stage.lower():
            for chemical in stage_info["chemicals"]:
                if disease in [d.lower() for d in chemical["disease"]]:
                    quantity = chemical["quantity"]
                    quantity_for_200_liters = quantity.split()[0] + ' ' + quantity.split()[1]
                    return {
                        "chemical_name": chemical["name"],
                        "quantity_for_200_liters": quantity_for_200_liters,
                        "brands": chemical["brands"]
                    }
    return None
@app.route('/classify_part', methods=['POST'])
def classify_part_route():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image = request.files['image']
    part_type = classify_plant_part(image)
    return jsonify({"part_type": part_type})
@app.route('/detect_disease', methods=['POST'])
def detect_disease_route():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image = request.files['image']
    part_type = classify_plant_part(image)
    if part_type != "leaf":
        return jsonify({"message": "Disease detection only applicable for leaves"}), 400
    disease_result = detect_disease(image)
    return jsonify({"disease": disease_result})
@app.route('/recommendation', methods=['POST'])
def recommendation_route():
    # Expecting only 'disease' in the request
    data = request.get_json()
    disease = data.get('disease')
    # Validate disease
    if not disease:
        return jsonify({"error": "'disease' is required."}), 400
    recommendation = get_chemicals(disease)
    if not recommendation:
        return jsonify({"message": "No recommendation found for the given disease."}), 200
    return jsonify(recommendation)
# @app.route('/products', methods=['GET'])
# def products_route():
#     try:
#         products = get_all_products()
#         return jsonify(products)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
@app.route('/products', methods=['GET'])
def products_route():
    try:
        products = get_all_products()
        print("Fetched products from DB:", products)
        return jsonify(products)
    except Exception as e:
        print("❌ Error in /products:", e)
        return jsonify({"error": str(e)}), 500
   


@app.route('/user-exists/<user_id>', methods=['GET'])
def user_exists_route(user_id):
    try:
        exists = user_exists(user_id)
        return jsonify({"exists": exists})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user/<user_id>', methods=['GET'])
def user_info_route(user_id):
    try:
        user = get_user_info(user_id)
        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/add-user', methods=['POST'])
def add_user_route():
    try:
        user_data = request.get_json()
        required_fields = [
            'userId', 'name', 'phone', 'pincode', 'state',
            'district', 'city', 'village_or_locality',
            'landmark', 'address_line'
        ]

        if not user_data or any(field not in user_data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        if user_exists(user_data['userId']):
            return jsonify({"message": "User already exists"}), 200

        inserted_id = add_user(user_data)
        return jsonify({"message": "User added", "user_id": inserted_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
    # command to run : flask run --host=172.18.1.50 --port=5000
