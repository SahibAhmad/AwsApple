

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os

# ------------------ MongoDB Setup ------------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    socketTimeoutMS=10000
)

try:
    client.admin.command("ping")
    print("✅ MongoDB connected successfully.")
except Exception as e:
    print("❌ MongoDB connection failed:", e)

# ------------------ Collections ------------------
db = client['leafy']
products_collection = db['products']
users_collection = db['users']
orders_collection = db['orders']
picked_orders_history_collection = db['picked_orders_history']

# ------------------ Product Functions ------------------

def get_all_products():
    products = list(products_collection.find())
    for product in products:
        product['_id'] = str(product['_id'])
    return products

def add_product(product_data: dict) -> str:
    result = products_collection.insert_one(product_data)
    return str(result.inserted_id)

def get_products_by_seller(seller_id: str):
    products = list(products_collection.find({"sellerId": seller_id}))
    for product in products:
        product['_id'] = str(product['_id'])
    return products

# ------------------ User Functions ------------------

def user_exists(user_id: str) -> bool:
    return users_collection.count_documents({"userId": user_id}) > 0

def get_user_info(user_id: str):
    user = users_collection.find_one({"userId": user_id})
    if user:
        user['_id'] = str(user['_id'])
        return user
    return None

def add_user(user_data: dict) -> str:
    result = users_collection.insert_one(user_data)
    return str(result.inserted_id)

def fetch_user_by_id(user_id: str):
    user = users_collection.find_one({"userId": user_id})
    if user:
        user.pop('_id', None)
        return user
    return None

def update_user_info(user_id: str, updated_data: dict) -> bool:
    result = users_collection.update_one(
        {"userId": user_id},
        {"$set": updated_data}
    )
    return result.matched_count > 0

# ------------------ Order Functions ------------------

def add_order(order_data: dict) -> str:
    order_data.update({
        "status": "Processing",
        "orderDate": datetime.now().strftime("%Y-%m-%d"),
        "expectedDelivery": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "isReceived": False
    })
    result = orders_collection.insert_one(order_data)
    return str(result.inserted_id)

def get_orders_by_user(user_id: str):
    orders = list(orders_collection.find({
        "userId": user_id,
        "isReceived": False
    }))
    for order in orders:
        order['_id'] = str(order['_id'])
    return orders

def update_order_status(order_id: str, status: str, picked_by: str = None) -> bool:
    update_data = {"status": status}
    if picked_by:
        update_data["pickedBy"] = picked_by

    result = orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

def mark_order_received(order_id: str) -> bool:
    result = picked_orders_history_collection.update_one(
        {"_id": order_id},  # match as string, not ObjectId
        {"$set": {"isReceived": True, "status": "Delivered"}}
    )
    return result.modified_count > 0




def update_order(order_id: str, update_data: dict) -> bool:
    result = orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

# ------------------ Seller Order Handling ------------------

def get_unpicked_orders():
    orders = list(orders_collection.find({"status": "Processing"}))
    for order in orders:
        order['_id'] = str(order['_id'])
    return orders

def pick_order(order_id: str, seller_id: str) -> bool:
    result = orders_collection.update_one(
        {"_id": ObjectId(order_id), "status": "Processing"},
        {"$set": {"status": "Picked", "pickedBy": seller_id}}
    )
    return result.modified_count > 0

def log_picked_order(order_id: str, seller_id: str) -> bool:
    order = orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        return False

    order['_id'] = str(order['_id'])
    order['pickedBy'] = seller_id
    order['pickedAt'] = datetime.now().isoformat()

    result = picked_orders_history_collection.insert_one(order)
    return result.acknowledged

def get_picked_orders_by_seller(seller_id: str):
    orders = list(orders_collection.find({
        "pickedBy": {"$exists": True, "$eq": seller_id}
    }))
    for order in orders:
        order['_id'] = str(order['_id'])
    return orders

def get_picked_orders_history_by_seller(seller_id: str):
    orders = list(picked_orders_history_collection.find({"pickedBy": seller_id}))
    for order in orders:
        order['_id'] = str(order['_id'])
    return orders
def update_order_status_in_db(order_id, new_status, picked_by=None):
    if not ObjectId.is_valid(order_id):
        return {"error": "Invalid order ID format"}, 400

    update_fields = {"status": new_status}
    if picked_by:
        update_fields["pickedBy"] = picked_by

    result = orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return {"error": "Order not found"}, 404

    if result.modified_count == 0:
        return {"message": "Order already marked as picked"}, 200

    return {"message": "Order status updated"}, 200


