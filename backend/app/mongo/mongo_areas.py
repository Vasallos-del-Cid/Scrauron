import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from ..models.area_de_trabajo import AreaDeTrabajo

# Conexión a MongoDB (como en mongo_fuentes.py)
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["baseDatosScrauron"]
coleccion = db["areas_de_trabajo"]

def get_mongo_collection():
    return coleccion

def get_areas():
    areas = list(coleccion.find())
    for a in areas:
        a["_id"] = str(a["_id"])
    return areas

def get_area_by_id(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    area = coleccion.find_one({"_id": ObjectId(area_id)})
    if area:
        area["_id"] = str(area["_id"])
    return area

def create_area(area):
    data = area.to_dict()
    if "_id" in data and data["_id"] is None:
        del data["_id"]
    insert_result = coleccion.insert_one(data)
    return insert_result

def delete_area(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    result = coleccion.delete_one({"_id": ObjectId(area_id)})
    return result.deleted_count

def update_area(area_id, data):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    if "_id" in data:
        del data["_id"]
    result = coleccion.update_one({"_id": ObjectId(area_id)}, {"$set": data})
    if result.matched_count == 0:
        return None
    updated = coleccion.find_one({"_id": ObjectId(area_id)})
    updated["_id"] = str(updated["_id"])
    return updated
