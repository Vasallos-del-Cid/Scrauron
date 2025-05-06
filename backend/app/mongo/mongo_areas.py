import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from ..models.area_de_trabajo import AreaDeTrabajo
from ..models.fuente import Fuente
from ..models.concepto_interes import ConceptoInteres
from .mongo_fuentes import get_fuente_by_id
from .mongo_conceptos import get_concepto_by_id

# Conexión a MongoDB
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["baseDatosScrauron"]
coleccion = db["areas_de_trabajo"]

# GET colección (opcional para acceso directo)
def get_mongo_collection():
    return coleccion

# GET todas las áreas
def get_areas():
    areas_raw = list(coleccion.find())
    return [AreaDeTrabajo.from_dict(a) for a in areas_raw]

# GET una sola área por ID
def get_area_by_id(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    area = coleccion.find_one({"_id": ObjectId(area_id)})
    if area:
        area["_id"] = str(area["_id"])
        return area
    return None

# POST crear nueva área
def create_area(area):
    data = area.to_dict()
    data.pop("_id", None)  # ❗️Eliminar _id siempre antes de insertar
    insert_result = coleccion.insert_one(data)
    return insert_result

# DELETE un área
def delete_area(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    result = coleccion.delete_one({"_id": ObjectId(area_id)})
    return result.deleted_count

# UPDATE un área
def update_area(area: AreaDeTrabajo):
    data = area.to_dict()
    area_id = data.pop("_id", None)

    if not area_id:
        raise ValueError("El área no tiene _id asignado. No se puede actualizar.")

    try:
        result = coleccion.update_one(
            {"_id": ObjectId(area_id)},
            {"$set": data}
        )
        if result.matched_count == 0:
            print(f"⚠️ No se encontró el área con _id: {area_id}")
        else:
            print(f"✅ Área actualizada correctamente: {area.nombre}")
    except Exception as e:
        print(f"❌ Error actualizando el área: {e}")

# PATCH agregar concepto a un área
def agregar_concepto_a_area(area_id: str, concepto_id: str):
    area_dict = get_area_by_id(area_id)
    if not area_dict:
        raise ValueError("Área no encontrada")

    area = AreaDeTrabajo.from_dict(area_dict)
    concepto = get_concepto_by_id(concepto_id)
    if not concepto:
        raise ValueError("Concepto no encontrado")

    if any(c._id == concepto._id for c in area.conceptos_interes):
        print(f"⚠️ El concepto ya está en el área: {concepto.nombre}")
        return False

    area.agregar_concepto(concepto)
    update_area(area)
    return True

# PATCH agregar fuente a un área
def agregar_fuente_a_area(area_id: str, fuente_id: str):
    area_dict = get_area_by_id(area_id)
    if not area_dict:
        raise ValueError("Área no encontrada")

    area = AreaDeTrabajo.from_dict(area_dict)
    fuente = get_fuente_by_id(fuente_id)
    if not fuente:
        raise ValueError("Fuente no encontrada")

    if any(f._id == fuente._id for f in area.fuentes):
        print(f"⚠️ La fuente ya está en el área: {fuente.nombre}")
        return False

    area.agregar_fuente(fuente)
    update_area(area)
    return True
