from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client['leafy']
products_collection = db['products']

products = [
    {
        "name": "Neem Oil Spray",
        "price": 180,
        "image": "https://example.com/images/neem_oil.jpg",
        "description": "Natural pesticide for controlling a wide range of insects and fungi.",
        "category": "Pesticide",
        "in_stock": True,
        "rating": 4.5,
        "reviews": 120
    },
    {
        "name": "Organic Apple Spray",
        "price": 150,
        "image": "https://example.com/images/apple_spray.jpg",
        "description": "Organic formula for protecting apples against diseases.",
        "category": "Pesticide",
        "in_stock": True,
        "rating": 4.2,
        "reviews": 87
    },
    {
        "name": "Leaf Protection Liquid",
        "price": 120,
        "image": "https://example.com/images/leaf_protection.jpg",
        "description": "Guards leaves from fungal and bacterial infections.",
        "category": "Fungicide",
        "in_stock": True,
        "rating": 4.0,
        "reviews": 65
    },
    {
        "name": "Anti-Fungal Treatment",
        "price": 200,
        "image": "https://example.com/images/fungal_treatment.jpg",
        "description": "Effective against a broad range of fungal diseases.",
        "category": "Fungicide",
        "in_stock": False,
        "rating": 4.6,
        "reviews": 140
    },
    {
        "name": "Fruit Growth Enhancer",
        "price": 250,
        "image": "https://example.com/images/fruit_growth.jpg",
        "description": "Stimulates fruit size and ripening speed naturally.",
        "category": "Tonic",
        "in_stock": True,
        "rating": 4.3,
        "reviews": 99
    },
    {
        "name": "Bio Pesticide Mix",
        "price": 160,
        "image": "https://example.com/images/bio_pesticide.jpg",
        "description": "Eco-friendly pesticide made from plant extracts.",
        "category": "Pesticide",
        "in_stock": True,
        "rating": 4.1,
        "reviews": 75
    },
    {
        "name": "Plant Tonic - 500ml",
        "price": 90,
        "image": "https://example.com/images/plant_tonic.jpg",
        "description": "General purpose tonic to boost plant health and resistance.",
        "category": "Tonic",
        "in_stock": True,
        "rating": 3.9,
        "reviews": 50
    },
    {
        "name": "Root Booster Granules",
        "price": 140,
        "image": "https://example.com/images/root_booster.jpg",
        "description": "Enhances root development and nutrient absorption.",
        "category": "Fertilizer",
        "in_stock": False,
        "rating": 4.7,
        "reviews": 150
    },
    {
        "name": "Fungal Shield for Leaves",
        "price": 170,
        "image": "https://example.com/images/fungal_shield.jpg",
        "description": "Protects leaves from common fungal infections.",
        "category": "Fungicide",
        "in_stock": True,
        "rating": 4.4,
        "reviews": 60
    },
    {
        "name": "Mosaic Virus Blocker",
        "price": 210,
        "image": "https://example.com/images/mosaic_blocker.jpg",
        "description": "Blocks virus infection in leaves and fruits.",
        "category": "Virus Control",
        "in_stock": True,
        "rating": 4.5,
        "reviews": 89
    },
    {
        "name": "Eco Guard Insecticide",
        "price": 195,
        "image": "https://example.com/images/eco_guard.jpg",
        "description": "Eco-friendly solution for pest control.",
        "category": "Insecticide",
        "in_stock": True,
        "rating": 4.3,
        "reviews": 77
    },
    {
        "name": "Scab Cure Formula",
        "price": 230,
        "image": "https://example.com/images/scab_cure.jpg",
        "description": "Cures scab infection effectively in apple crops.",
        "category": "Fungicide",
        "in_stock": True,
        "rating": 4.8,
        "reviews": 102
    }
]
products_collection.insert_many(products)
print("✅ Seeded Products collection with 12 detailed items.")
