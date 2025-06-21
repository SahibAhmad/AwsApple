import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
# Internal modules
from db import (
    add_product, get_all_products, get_orders_by_user, get_picked_orders_by_seller, get_picked_orders_history_by_seller, get_products_by_seller, get_unpicked_orders, log_picked_order, mark_order_received, pick_order, update_order, update_order_status, update_order_status_in_db, user_exists, get_user_info,
    add_user, fetch_user_by_id, update_user_info,
    add_order  # ➕ Import add_order
)
from Data import data
# Load environment variables
load_dotenv()
# Flask setup
app = Flask(__name__)
CORS(app)
# Load models
part_classifier_model = tf.keras.models.load_model('../model-train/classifier.h5')
disease_detection_model = tf.keras.models.load_model('../model-train/apple_disease_detector.h5')
# Constants
part_classes = ['leaf', 'non-leaf']
disease_classes = ['alternaria', 'healthy', 'mossaic', 'scab']
# Utility functions
def preprocess_image(image, target_size=(224, 224)):
    image = Image.open(image).convert('RGB').resize(target_size)
    image = np.expand_dims(preprocess_input(np.array(image)), axis=0)
    return image
def classify_plant_part(image):
    predictions = part_classifier_model.predict(preprocess_image(image))
    return "non-leaf" if predictions > 0.5 else "leaf"
def detect_disease(image):
    predictions = disease_detection_model.predict(preprocess_image(image))
    return disease_classes[np.argmax(predictions)]
def get_chemicals(disease=None):
    stage = "Fruit development"
    for stage_info in data["spray_schedule"]:
        if stage_info["stage"].lower() == stage.lower():
            for chemical in stage_info["chemicals"]:
                if disease in [d.lower() for d in chemical["disease"]]:
                    quantity = chemical["quantity"]
                    quantity_for_200_liters = " ".join(quantity.split()[:2])
                    return {
                        "chemical_name": chemical["name"],
                        "quantity_for_200_liters": quantity_for_200_liters,
                        "brands": chemical["brands"]
                    }
    return None
# ------------------- ROUTES -------------------
@app.route('/classify_part', methods=['POST'])
def classify_part_route():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    part_type = classify_plant_part(request.files['image'])
    return jsonify({"part_type": part_type})
@app.route('/detect_disease', methods=['POST'])
def detect_disease_route():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image = request.files['image']
    if classify_plant_part(image) != "leaf":
        return jsonify({"message": "Disease detection only applicable for leaves"}), 400
    return jsonify({"disease": detect_disease(image)})
@app.route('/recommendation', methods=['POST'])
def recommendation_route():
    disease = request.get_json().get('disease')
    if not disease:
        return jsonify({"error": "'disease' is required."}), 400
    recommendation = get_chemicals(disease)
    if not recommendation:
        return jsonify({"message": "No recommendation found for the given disease."}), 200
    return jsonify(recommendation)
@app.route('/products', methods=['GET'])
def products_route():
    try:
        return jsonify(get_all_products())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/user-exists/<user_id>', methods=['GET'])
def user_exists_route(user_id):
    try:
        return jsonify({"exists": user_exists(user_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/user/<user_id>', methods=['GET'])
def user_info_route(user_id):
    try:
        user = get_user_info(user_id)
        return jsonify(user) if user else ({"error": "User not found"}, 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/add-user', methods=['POST'])
def add_user_route():
    try:
        user_data = request.get_json()
        required = ['userId', 'name', 'phone', 'pincode', 'state',
                    'district', 'city', 'village_or_locality', 'landmark', 'address_line']
        if not user_data or any(f not in user_data for f in required):
            return jsonify({"error": "Missing required fields"}), 400
        if user_exists(user_data['userId']):
            return jsonify({"message": "User already exists"}), 200
        user_id = add_user(user_data)
        return jsonify({"message": "User added", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/get-user/<user_id>', methods=['GET'])
def get_user_route(user_id):
    try:
        user = fetch_user_by_id(user_id)
        return (jsonify(user), 200) if user else ({"error": "User not found"}, 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/update-user/<user_id>', methods=['PUT'])
def update_user_route(user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        if not update_user_info(user_id, data):
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/place-order', methods=['POST'])
def place_order_route():
    try:
        data = request.get_json()
        required = ['userId', 'items', 'paymentMethod', 'totalAmount']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        user = fetch_user_by_id(data['userId'])
        if not user:
            return jsonify({"error": "User not found"}), 404
        order = {
            "userId": data["userId"],
            "userDetails": user,
            "items": data["items"],
            "paymentMethod": data["paymentMethod"],
            "totalAmount": data["totalAmount"],
            "status": "Pending"
        }
        order_id = add_order(order)
        return jsonify({"message": "Order placed", "order_id": order_id}), 201
    except Exception as e:
        print("❌ Error placing order:", e)
        return jsonify({"error": "Server error"}), 500
@app.route('/orders/<user_id>', methods=['GET'])
def get_user_orders(user_id):
    try:
        orders = get_orders_by_user(user_id)
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# to be combined
@app.route('/mark-order-received/<order_id>', methods=['PUT'])
def mark_order_received_route(order_id):
    try:
        if not mark_order_received(order_id):
            return jsonify({"error": "Order not found or already received"}), 404
        return jsonify({"message": "Order marked as received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#combined version-----------------------------------------------------
# @app.route('/mark-order-received/<order_id>', methods=['PUT'])
# def mark_order_received_route(order_id):
#     try:
#         if not mark_order_received(order_id):
#             return jsonify({"error": "Order not found or already received"}), 404
#         return jsonify({"message": "Order marked as received"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500






@app.route('/unpicked-orders', methods=['GET'])
def unpicked_orders_route():
    try:
        return jsonify(get_unpicked_orders())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/pick-order/<order_id>', methods=['PUT'])
def pick_order_route(order_id):
    try:
        data = request.get_json()
        seller_id = data.get("sellerId")
        if not seller_id:
            return jsonify({"error": "Missing sellerId"}), 400
        if not pick_order(order_id, seller_id):
            return jsonify({"error": "Order not found or already picked"}), 404
        log_picked_order(order_id, seller_id)
        return jsonify({"message": "Order marked as picked"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/picked-orders/<seller_id>', methods=['GET'])
def picked_orders_route(seller_id):
    try:
        picked = get_picked_orders_by_seller(seller_id)
        return jsonify(picked)
    except Exception as e:
        print("Error in /picked-orders:", e)
        return jsonify({"error": str(e)}), 500
@app.route('/picked-orders-history/<seller_id>', methods=['GET'])
def picked_orders_history_route(seller_id):
    try:
        orders = get_picked_orders_history_by_seller(seller_id)
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ------------------ Seller Routes ------------------
@app.route('/add-product', methods=['POST'])
def add_product_route():
    try:
        data = request.get_json()
        required = ['name', 'price', 'image', 'description', 'category', 'sellerId']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400
        product_id = add_product(data)
        return jsonify({"message": "Product added", "product_id": product_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/seller-products/<seller_id>', methods=['GET'])
def get_seller_products_route(seller_id):
    try:
        products = get_products_by_seller(seller_id)
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # this is something to be changed
# @app.route('/update-order-status/<order_id>', methods=['PUT'])
# def update_order_status_route(order_id):
#     try:
#         data = request.get_json()
#         new_status = data.get("status")
#         picked_by = data.get("pickedBy")  # Optional

#         if not new_status:
#             return jsonify({"error": "Missing 'status'"}), 400

#         result, status_code = update_order_status_in_db(order_id, new_status, picked_by)

#         # ✅ If order is successfully picked, log to picked_orders_history
#         if new_status == "Picked" and status_code == 200:
#             from db import log_picked_order
#             log_picked_order(order_id, picked_by)

#         return jsonify(result), status_code

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/update-order-status/<order_id>', methods=['PUT'])
def update_order_status_route(order_id):
    try:
        data = request.get_json()
        new_status = data.get("status")
        picked_by = data.get("pickedBy")  # Optional

        if not new_status:
            return jsonify({"error": "Missing 'status'"}), 400

        result, status_code = update_order_status_in_db(order_id, new_status, picked_by)

        # ✅ Log only if status is "Picked"
        if new_status == "Picked" and status_code == 200 and picked_by:
            from db import log_picked_order
            log_picked_order(order_id, picked_by)

        return jsonify(result), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
## ✅ app.py (complete and final version)
