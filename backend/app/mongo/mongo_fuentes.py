from flask import jsonify

from .mongo_utils import get_collection
from ..models.fuente import Fuente
from bson import ObjectId

def get_fuentes():
    fuentes = list(get_collection("fuentes").find())
    for f in fuentes:
        f["_id"] = str(f["_id"])
    return fuentes



def get_fuente_by_id(fuente_id: str):
    if not ObjectId.is_valid(fuente_id):
        return None
    raw = get_collection("fuentes").find_one({"_id": ObjectId(fuente_id)})
    if raw:
        raw["_id"] = str(raw["_id"])  # convertir _id para que from_dict lo maneje como string
        return Fuente.from_dict(raw)
    return None


def create_fuente(fuente):
    print(fuente)
    data = fuente.to_dict()
    print("DATA: ", data)
    # Verificar si ya existe una fuente con la misma URL
    if get_collection("fuentes").find_one({"url": data["url"]}):
        return jsonify({"error": "Ya existe una fuente con esa URL"}), 409
    else:
        print("En else")
        insert_result = get_collection("fuentes").insert_one(data)
        print(insert_result)
        return jsonify({
            "_id": str(insert_result.inserted_id),
            "nombre": data["nombre"],
            "url": data["url"]
        }), 201




def delete_fuente(fuente_id):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    result = get_collection("fuentes").delete_one({"_id": ObjectId(fuente_id)})
    return result.deleted_count


def update_fuente(fuente_id, data):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    if "_id" in data:
        del data["_id"]

    result = get_collection("fuentes").update_one(
        {"_id": ObjectId(fuente_id)},
        {"$set": data}
    )

    if result.matched_count == 0:
        return None

    # Recuperar el documento actualizado
    updated_fuente = get_collection("fuentes").find_one({"_id": ObjectId(fuente_id)})
    updated_fuente["_id"] = str(updated_fuente["_id"])
    return updated_fuente
