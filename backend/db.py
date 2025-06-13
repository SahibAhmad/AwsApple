

from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime, timedelta

# MongoDB setup
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

# Database and collections
db = client['leafy']
products_collection = db['products']
users_collection = db['users']
orders_collection = db['orders']

# ------------------ Products ------------------

def get_all_products():
    products = list(products_collection.find())
    for product in products:
        product['_id'] = str(product['_id'])
    return products

# ------------------ Users ------------------

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
        user.pop('_id', None)  # exclude internal _id
        return user
    return None

def update_user_info(user_id: str, updated_data: dict) -> bool:
    result = users_collection.update_one(
        {"userId": user_id},
        {"$set": updated_data}
    )
    return result.matched_count > 0

# ------------------ Orders ------------------

def add_order(order_data: dict) -> str:
    order_data['status'] = 'Processing'
    order_data['orderDate'] = datetime.now().strftime("%Y-%m-%d")
    order_data['expectedDelivery'] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    order_data['isReceived'] = False  # ⬅️ Added field
    result = orders_collection.insert_one(order_data)
    return str(result.inserted_id)


def get_orders_by_user(user_id: str):
    orders = list(orders_collection.find({
        "userId": user_id,
        "isReceived": False  # ⬅️ Only show unreceived orders
    }))
    for order in orders:
        order['_id'] = str(order['_id'])
    return orders


def update_order_status(order_id: str, new_status: str) -> bool:
    result = orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": new_status}}
    )
    return result.modified_count > 0
def mark_order_received(order_id: str) -> bool:
    result = orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"isReceived": True}}
    )
    return result.modified_count > 0
