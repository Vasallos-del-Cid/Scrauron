import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from ..models.publicacion import Publicacion

# Conexión a MongoDB (igual que en fuentes)
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["baseDatosScrauron"]
coleccion = db["publicaciones"]

def get_mongo_collection():
    return coleccion

def get_publicaciones():
    publicaciones = list(coleccion.find())
    for p in publicaciones:
        p["_id"] = str(p["_id"])
    return publicaciones

def get_publicacion_by_id(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    pub = coleccion.find_one({"_id": ObjectId(pub_id)})
    if pub:
        pub["_id"] = str(pub["_id"])
    return pub

def create_publicacion(publicacion):
    data = publicacion.to_dict()
    if "_id" in data and data["_id"] is None:
        del data["_id"]
    insert_result = coleccion.insert_one(data)
    return insert_result

def delete_publicacion(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    result = coleccion.delete_one({"_id": ObjectId(pub_id)})
    return result.deleted_count

def update_publicacion(pub_id, data):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    if "_id" in data:
        del data["_id"]
    result = coleccion.update_one({"_id": ObjectId(pub_id)}, {"$set": data})
    if result.matched_count == 0:
        return None
    updated = coleccion.find_one({"_id": ObjectId(pub_id)})
    updated["_id"] = str(updated["_id"])
    return updated
