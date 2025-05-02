import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["baseDatosScrauron"]
coleccion = db["noticias"]    