import logging
from bson import ObjectId
from .mongo_utils import get_collection
from ..models.area_impacto import AreaImpacto
from ..mongo.mongo_areas import get_area_by_id

# --------------------------------------------------
def get_areas_impacto():
    areas_raw = list(get_collection("areas_impacto").find())
    for a in areas_raw:
        a["_id"] = str(a["_id"])
        if "area_id" in a and isinstance(a["area_id"], ObjectId):
            a["area_id"] = str(a["area_id"])
    return [AreaImpacto.from_dict(a) for a in areas_raw]

# --------------------------------------------------
def get_area_impacto_by_id(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    area = get_collection("areas_impacto").find_one({"_id": ObjectId(area_id)})
    if area:
        area["_id"] = str(area["_id"])
        if "area_id" in area and isinstance(area["area_id"], ObjectId):
            area["area_id"] = str(area["area_id"])
        return area
    return None

# --------------------------------------------------
def create_area_impacto(area):
    data = area.to_dict()
    data.pop("_id", None)
    if data.get("area_id"):
        data["area_id"] = ObjectId(data["area_id"])  # 👈 conversión clave
    insert_result = get_collection("areas_impacto").insert_one(data)
    return insert_result

# --------------------------------------------------
def delete_area_impacto(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    result = get_collection("areas_impacto").delete_one({"_id": ObjectId(area_id)})
    return result.deleted_count

# --------------------------------------------------
def update_area_impacto(area: AreaImpacto):
    data = area.to_dict()
    area_id = data.pop("_id", None)

    if not area_id:
        raise ValueError("El área no tiene _id asignado. No se puede actualizar.")

    try:
        oid = ObjectId(area_id)
    except Exception as e:
        raise ValueError(f"ID de área inválido: {area_id}") from e

    if data.get("area_id"):
        data["area_id"] = ObjectId(data["area_id"])

    result = get_collection("areas_impacto").update_one(
        {"_id": oid},
        {"$set": data}
    )

    if result.matched_count == 0:
        logging.warning(f"⚠️ No se encontró el área de impacto con _id: {area_id}")
    elif result.modified_count == 0:
        logging.info("ℹ️ Área de impacto sin cambios.")
    else:
        logging.info(f"✅ Área de impacto actualizada: {area.nombre}")

# --------------------------------------------------
def update_area_impacto(area: AreaImpacto):
    data = area.to_dict()
    area_id = data.pop("_id", None)

    if not area_id:
        raise ValueError("El área no tiene _id asignado. No se puede actualizar.")

    try:
        oid = ObjectId(area_id)
    except Exception as e:
        raise ValueError(f"ID de área inválido: {area_id}") from e

    # Convertir area_id interno a ObjectId si es string
    if "area_id" in data and isinstance(data["area_id"], str) and ObjectId.is_valid(data["area_id"]):
        data["area_id"] = ObjectId(data["area_id"])

    result = get_collection("areas_impacto").update_one(
        {"_id": oid},
        {"$set": data}
    )

    if result.matched_count == 0:
        logging.warning(f"⚠️ No se encontró el área de impacto con _id: {area_id}")
    elif result.modified_count == 0:
        logging.info("ℹ️ Área de impacto sin cambios.")
    else:
        logging.info(f"✅ Área de impacto actualizada: {area.nombre}")

# --------------------------------------------------
from app.mongo.mongo_areas import get_area_by_id  # Función que espera un ObjectId

def get_areas_impacto_by_area_trabajo_id(area_trabajo_id: str):
    # Validar y convertir el ID a ObjectId
    if not ObjectId.is_valid(area_trabajo_id):
        raise ValueError("ID de área de trabajo no válido")
    oid = ObjectId(area_trabajo_id)

    # Validar existencia del área usando la función centralizada
    if not get_area_by_id(oid):
        raise ValueError("No existe un área de trabajo con ese ID")

    # Buscar las áreas de impacto relacionadas
    areas_raw = list(get_collection("areas_impacto").find({"area_id": oid}))

    # Formatear los resultados para que sean serializables
    for a in areas_raw:
        a["_id"] = str(a["_id"])
        if "area_id" in a and isinstance(a["area_id"], ObjectId):
            a["area_id"] = str(a["area_id"])

    return [AreaImpacto.from_dict(a) for a in areas_raw]

