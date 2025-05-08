# mongo_fuentes.py

# Este módulo gestiona operaciones CRUD sobre documentos de tipo "Fuente" en MongoDB.
# Cada fuente representa un sitio web o dominio monitorizado para extraer noticias.

import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
from flask import jsonify, request
from ..models.fuente import Fuente
from bson import ObjectId

# --------------------------------------------------
# Cargar las variables de entorno y conectar a MongoDB
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

# Selección de base de datos y colección
db = client["baseDatosScrauron"]
coleccion = db["fuentes"]

# --------------------------------------------------
# Devuelve el objeto de colección (útil para acceso directo externo)
def get_mongo_collection():
    return coleccion

# --------------------------------------------------
# Recupera todas las fuentes registradas en la colección
def get_fuentes():
    fuentes = list(coleccion.find())
    for f in fuentes:
        f["_id"] = str(f["_id"])  # Convertir ObjectId para que sea serializable en JSON
    return fuentes

# --------------------------------------------------
# Recupera una fuente concreta por su ID
def get_fuente_by_id(fuente_id: str):
    if not ObjectId.is_valid(fuente_id):
        return None
    raw = coleccion.find_one({"_id": ObjectId(fuente_id)})
    if raw:
        raw["_id"] = str(raw["_id"])  # Asegura compatibilidad con from_dict
        return Fuente.from_dict(raw)
    return None

# --------------------------------------------------
# Crea una nueva fuente si no existe una con la misma URL
def create_fuente(fuente):
    print(fuente)
    data = fuente.to_dict()
    print("DATA: ", data)

    # Verificar existencia previa por URL
    if coleccion.find_one({"url": data["url"]}):
        return jsonify({"error": "Ya existe una fuente con esa URL"}), 409
    else:
        print("En else")
        insert_result = coleccion.insert_one(data)
        print(insert_result)
        return jsonify({
            "_id": str(insert_result.inserted_id),
            "nombre": data["nombre"],
            "url": data["url"]
        }), 201

# --------------------------------------------------
# Elimina una fuente de la colección por su ID
def delete_fuente(fuente_id):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    result = coleccion.delete_one({"_id": ObjectId(fuente_id)})
    return result.deleted_count

# --------------------------------------------------
# Actualiza parcialmente una fuente existente
def update_fuente(fuente_id, data):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    # Previene la sobreescritura del _id
    if "_id" in data:
        del data["_id"]

    result = coleccion.update_one(
        {"_id": ObjectId(fuente_id)},
        {"$set": data}
    )

    if result.matched_count == 0:
        return None

    # Devolver la fuente actualizada
    updated_fuente = coleccion.find_one({"_id": ObjectId(fuente_id)})
    updated_fuente["_id"] = str(updated_fuente["_id"])
    return updated_fuente
