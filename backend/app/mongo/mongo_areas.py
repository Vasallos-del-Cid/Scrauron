from bson import ObjectId

from .mongo_utils import get_collection
from ..models.area_de_trabajo import AreaDeTrabajo

# GET todas las áreas
def get_areas():
    areas_raw = list(get_collection("areas_de_trabajo").find())
    return [AreaDeTrabajo.from_dict(a) for a in areas_raw]


# GET una sola área por ID
def get_area_by_id(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    area = get_collection("areas_de_trabajo").find_one({"_id": ObjectId(area_id)})
    if area:
        area["_id"] = str(area["_id"])
        return area
    return None


# POST crear nueva área
def create_area(area):
    data = area.to_dict()
    data.pop("_id", None)  # ❗️Eliminar _id siempre antes de insertar
    insert_result = get_collection("areas_de_trabajo").insert_one(data)
    return insert_result


# DELETE un área
def delete_area(area_id):
    if not ObjectId.is_valid(area_id):
        raise ValueError("ID no válido")
    result = get_collection("areas_de_trabajo").delete_one({"_id": ObjectId(area_id)})
    return result.deleted_count


# UPDATE un área
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
        print(f"⚠️ No se encontró el área con _id: {area_id}")
    elif result.modified_count == 0:
        print(f"ℹ️ Área encontrada pero sin cambios.")
    else:
        print(f"✅ Área actualizada correctamente: {area.nombre}")


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
        print(f"⚠️ No se encontró el área con _id: {area_id}")
    elif result.modified_count == 0:
        print(f"ℹ️ El área ya estaba actualizada, sin cambios.")
    else:
        print(f"✅ Área actualizada correctamente.")


# PATCH agregar concepto a un área (solo _id)
def agregar_concepto_a_area(area_id: str, concepto_id: str):
    area_dict = get_area_by_id(area_id)
    if not area_dict:
        raise ValueError("Área no encontrada")

    concepto_oid = ObjectId(concepto_id)

    conceptos_actuales = area_dict.get("conceptos_interes_ids", [])

    # Asegurar comparación correcta entre ObjectIds
    if concepto_oid in conceptos_actuales:
        print(f"⚠️ El concepto ya está en el área (id: {concepto_id})")
        return False

    conceptos_actuales.append(concepto_oid)
    update_area_dict(area_id, {"conceptos_interes_ids": conceptos_actuales})

    return True


# PATCH agregar fuente a un área (solo _id)
def agregar_fuente_a_area(area_id: str, fuente_id: str):
    area_dict = get_area_by_id(area_id)
    if not area_dict:
        raise ValueError("Área no encontrada")

    fuente_oid = ObjectId(fuente_id)

    fuentes_actuales = area_dict.get("fuentes_ids", [])

    if fuente_oid in fuentes_actuales:
        print(f"⚠️ La fuente ya está en el área (id: {fuente_id})")
        return False

    fuentes_actuales.append(fuente_oid)
    update_area_dict(area_id, {"fuentes_ids": fuentes_actuales})

    return True
