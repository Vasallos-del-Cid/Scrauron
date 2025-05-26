import logging

from bson import ObjectId

from .mongo_utils import get_collection
from ..models.area_de_trabajo import AreaDeTrabajo

# --------------------------------------------------
# Recupera todas las áreas de trabajo como instancias de AreaDeTrabajo
def get_areas():
    areas_raw = list(get_collection("areas_de_trabajo").find())
    return [AreaDeTrabajo.from_dict(a) for a in areas_raw]

# --------------------------------------------------
# Recupera una única área por su ID
def get_area_by_id(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    area = get_collection("areas_de_trabajo").find_one({"_id": ObjectId(area_id)})
    if area:
        area["_id"] = str(area["_id"])
        return area
    return None

# --------------------------------------------------
# Crea una nueva área de trabajo en la colección
def create_area(area):
    data = area.to_dict()
    data.pop("_id", None)  # borrar _id si es None para evitar error al insertar
    insert_result = get_collection("areas_de_trabajo").insert_one(data)
    return insert_result

# --------------------------------------------------
# Elimina un área de trabajo por su ID
def delete_area(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    result = get_collection("areas_de_trabajo").delete_one({"_id": ObjectId(area_id)})
    return result.deleted_count

# --------------------------------------------------
# Actualiza por completo un objeto de tipo AreaDeTrabajo
def update_area(area: AreaDeTrabajo):
    data = area.to_dict()
    area_id = data.pop("_id", None)

    if not area_id:
        raise ValueError("El área no tiene _id asignado. No se puede actualizar.")

    try:
        oid = ObjectId(area_id)
    except Exception as e:
        raise ValueError(f"ID de área inválido: {area_id}") from e

    result = get_collection("areas_de_trabajo").update_one(
        {"_id": oid},
        {"$set": data}
    )

    if result.matched_count == 0:
        logging.warning(f"⚠️ No se encontró el área con _id: {area_id}")
    elif result.modified_count == 0:
        logging.info(f"ℹ️ Área encontrada pero sin cambios.")
    else:
        logging.info(f"✅ Área actualizada correctamente: {area.nombre}")

# --------------------------------------------------
# Actualiza parcialmente un área usando un diccionario con campos modificados
def update_area_dict(area_id: str, campos_actualizados: dict):
    try:
        oid = ObjectId(area_id)
    except Exception as e:
        raise ValueError(f"ID de área inválido: {area_id}") from e

    result = get_collection("areas_de_trabajo").update_one(
        {"_id": oid},
        {"$set": campos_actualizados}
    )

    if result.matched_count == 0:
        logging.warning(f"⚠️ No se encontró el área con _id: {area_id}")
    elif result.modified_count == 0:
        logging.info(f"ℹ️ El área ya estaba actualizada, sin cambios.")
    else:
        logging.info(f"✅ Área actualizada correctamente.")

# --------------------------------------------------
# Añade un concepto a una área (referencia por ID)
def agregar_concepto_a_area(area_id: str, concepto_id: str):
    area_dict = get_area_by_id(area_id)
    if not area_dict:
        raise ValueError("Área no encontrada")

    concepto_oid = ObjectId(concepto_id)
    conceptos_actuales = area_dict.get("conceptos_interes_ids", [])

    if concepto_oid in conceptos_actuales:
        logging.warning(f"⚠️ El concepto ya está en el área (id: {concepto_id})")
        return False

    conceptos_actuales.append(concepto_oid)
    update_area_dict(area_id, {"conceptos_interes_ids": conceptos_actuales})

    return True

# --------------------------------------------------
# Añade una fuente a un área (referencia por ID)
def agregar_fuente_a_area(area_id: str, fuente_id: str):
    area_dict = get_area_by_id(area_id)
    if not area_dict:
        raise ValueError("Área no encontrada")

    fuente_oid = ObjectId(fuente_id)
    fuentes_actuales = area_dict.get("fuentes_ids", [])

    if fuente_oid in fuentes_actuales:
        logging.warning(f"⚠️ La fuente ya está en el área (id: {fuente_id})")
        return False

    fuentes_actuales.append(fuente_oid)
    update_area_dict(area_id, {"fuentes_ids": fuentes_actuales})

    return True

