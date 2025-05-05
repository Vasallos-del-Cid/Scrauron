import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
from flask import jsonify, request
from ..models.fuente import Fuente
from bson import ObjectId

# Cargar variables del entorno desde .env
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client["baseDatosScrauron"]
coleccion = db["fuentes"]

def get_mongo_collection():
    return coleccion

def get_fuentes():
    fuentes = list(coleccion.find())
    for f in fuentes:
        f["_id"] = str(f["_id"])
    return fuentes

def get_fuente_by_id(fuente_id):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    fuente = coleccion.find_one({"_id": ObjectId(fuente_id)})
    if fuente:
        fuente["_id"] = str(fuente["_id"])
    return fuente

def create_fuente(fuente):
    data = fuente.to_dict()

    # Eliminar manualmente _id si está presente y es None
    if "_id" in data and data["_id"] is None:
        del data["_id"]

    insert_result = coleccion.insert_one(data)
    return insert_result


def delete_fuente(fuente_id):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    result = coleccion.delete_one({"_id": ObjectId(fuente_id)})
    return result.deleted_count


def update_fuente(fuente_id, data):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    if "_id" in data:
        del data["_id"]

    result = coleccion.update_one(
        {"_id": ObjectId(fuente_id)},
        {"$set": data}
    )

    if result.matched_count == 0:
        return None

    # Recuperar el documento actualizado
    updated_fuente = coleccion.find_one({"_id": ObjectId(fuente_id)})
    updated_fuente["_id"] = str(updated_fuente["_id"])
    return updated_fuente
