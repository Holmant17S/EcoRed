import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "ecored_circular_db")

client = MongoClient(MONGODB_URI) if MONGODB_URI else None
db = client[MONGODB_DB_NAME] if client is not None else None
material_listings_collection = db["material_listings"] if db is not None else None
