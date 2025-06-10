
from pymongo import MongoClient
import os
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
db = client['leafy']
products_collection = db['products']
users_collection = db["users"]
def get_all_products():
    products = list(products_collection.find())
    for product in products:
        product['_id'] = str(product['_id'])
    return products



def user_exists(user_id: str) -> bool:
    return users_collection.count_documents({"userId": user_id}) > 0
def get_user_info(user_id: str):
    user = users_collection.find_one({"userId": user_id})
    if user:
        user['id'] = str(user['_id'])  
        return user
    return None
def add_user(user_data: dict):
    """Inserts a new user into the database."""
    result = users_collection.insert_one(user_data)
    return str(result.inserted_id)
