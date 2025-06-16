from flask import Blueprint, request, jsonify
from ..models.concepto_interes import ConceptoInteres
from ..models.modelUtils.SerializeJson import SerializeJson
from ..mongo.mongo_areas import agregar_concepto_a_area
from bson import ObjectId
from ..mongo.mongo_conceptos import (
    get_conceptos,
    get_concepto_by_id,
    create_concepto,
    update_concepto,
    delete_concepto,
    add_descripcion_llm,
    add_keywords_llm,
    get_conceptos_by_area_id
)

api_conceptos = Blueprint('api_conceptos', __name__)

# Utilidad para convertir ObjectId a string
def _convert_objectid(doc):
    if not isinstance(doc, dict):
        doc = dict(doc)
    if "_id" in doc and isinstance(doc["_id"], object):
        doc["_id"] = str(doc["_id"])
    return doc

# Obtiene todos los conceptos registrados
@api_conceptos.route('/conceptos', methods=['GET'])
@SerializeJson
def get_conceptos_endpoint():
    try:
        conceptos = get_conceptos()
        return conceptos,200
    except Exception as e:
        return {"error": str(e)},500

# Obtiene un concepto por su ID
@api_conceptos.route('/conceptos/<concepto_id>', methods=['GET'])
@SerializeJson
def get_concepto_endpoint(concepto_id):
    try:
        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return {"error": "Concepto no encontrado"},404
        return _convert_objectid(concepto.to_dict()),200
    except ValueError as ve:
        return {"error": str(ve)},400

# Crea un nuevo concepto
@api_conceptos.route('/conceptos', methods=['POST'])
@SerializeJson
def create_concepto_endpoint():
    data = request.get_json()
    try:
        concepto = ConceptoInteres.from_dict(data)
        insert_result = create_concepto(concepto)

        if insert_result is None or not hasattr(insert_result, "inserted_id"):
            return {"error": "Error al insertar el concepto"},500

        concepto._id = str(insert_result.inserted_id)
        return _convert_objectid(concepto.to_dict()),201
    except Exception as e:
        return {"error": str(e)},400

# Actualiza parcialmente un concepto
@api_conceptos.route('/conceptos/<concepto_id>', methods=['PATCH'])
@SerializeJson
def patch_concepto_endpoint(concepto_id):
    data = request.get_json()
    try:
        concepto = ConceptoInteres.from_dict(data)
        concepto._id = concepto_id
        update_concepto(concepto)
        return _convert_objectid(concepto.to_dict()),200
    except ValueError as ve:
        return {"error": str(ve)},400
    except Exception as e:
        return {"error": str(e)},500

# Elimina un concepto por su ID
@api_conceptos.route('/conceptos/<concepto_id>', methods=['DELETE'])
@SerializeJson
def delete_concepto_endpoint(concepto_id):
    try:
        deleted = delete_concepto(concepto_id)
        if deleted == 0:
            return {"error": "Concepto no encontrado"},404
        return '', 204
    except ValueError as ve:
        return {"error": str(ve)},400

# Genera una descripción para el concepto utilizando LLM
@api_conceptos.route('/conceptos/<concepto_id>/generar_descripcion', methods=['PATCH'])
@SerializeJson
def generar_descripcion_concepto(concepto_id):
    concepto = get_concepto_by_id(concepto_id)
    if not concepto:
        return {"error": "Concepto no encontrado"},404

    add_descripcion_llm(concepto)

    return concepto.to_dict(),200

# Genera keywords para un concepto con base en una nueva descripción
@api_conceptos.route('/conceptos/<concepto_id>/generar_keywords', methods=['PATCH'])
@SerializeJson
def generar_keywords_concepto(concepto_id):
    try:
        data = request.get_json()
        nueva_descripcion = data.get("descripcion")

        if not nueva_descripcion:
            return {"error": "Debe proporcionarse una descripción para generar keywords"},400

        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return {"error": "Concepto no encontrado"},404

        concepto.descripcion = nueva_descripcion
        add_keywords_llm(concepto)

        return concepto.to_dict(),200

    except Exception as e:
        return {"error": f"Error al generar keywords para el concepto: {str(e)}"},500

# Actualiza las keywords de un concepto y lo vincula a un área
@api_conceptos.route('/conceptos/<area_id>/keywords_aceptadas', methods=['PATCH'])
@SerializeJson
def update_keywords_ids_en_area_endpoint(area_id):
    try:
        if not ObjectId.is_valid(area_id):
            return {"error": "ID de área no válido."},400

        data = request.get_json()
        concepto_id = data.get("_id")
        if not concepto_id:
            return {"error": "El concepto debe contener _id."},400

        if not ObjectId.is_valid(concepto_id):
            return {"error": f"ID de concepto no válido: {concepto_id}"},400

        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return {"error": "Concepto no encontrado"},404

        keywords_ids_raw = data.get("keywords_ids", [])
        if not isinstance(keywords_ids_raw, list):
            return {"error": "keywords_ids debe ser una lista."},400

        keywords_ids = []
        for kid in keywords_ids_raw:
            if not ObjectId.is_valid(str(kid)):
                return {"error": f"ID de keyword no válido: {kid}"},400
            keywords_ids.append(ObjectId(str(kid)))

        concepto.keywords_ids = keywords_ids
        update_concepto(concepto)

        agregar_concepto_a_area(area_id, concepto._id)

        return concepto.to_dict(),200

    except Exception as e:
        return {"error": f"Error al actualizar keywords y vincular área: {str(e)}"},500

# Añade una keyword a un concepto
@api_conceptos.route('/conceptos/<concepto_id>/keywords', methods=['POST'])
@SerializeJson
def add_keyword_to_concepto(concepto_id):
    try:
        data = request.get_json()
        keyword_id = data.get("keyword_id")

        if not keyword_id or not ObjectId.is_valid(keyword_id):
            return {"error": "keyword_id no válido"},400

        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return {"error": "Concepto no encontrado"},404

        keyword_oid = ObjectId(keyword_id)

        if keyword_oid not in concepto.keywords_ids:
            concepto.keywords_ids.append(keyword_oid)
            update_concepto(concepto)

        return concepto.to_dict(),200

    except Exception as e:
        return {"error": f"Error al agregar keyword al concepto: {str(e)}"},500

# Elimina una keyword de un concepto
@api_conceptos.route('/conceptos/<concepto_id>/keywords/<keyword_id>', methods=['DELETE'])
@SerializeJson
def remove_keyword_from_concepto(concepto_id, keyword_id):
    try:
        if not ObjectId.is_valid(keyword_id):
            return {"error": "keyword_id no válido"},400

        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return {"error": "Concepto no encontrado"},404

        keyword_oid = ObjectId(keyword_id)

        if keyword_oid in concepto.keywords_ids:
            concepto.keywords_ids.remove(keyword_oid)
            update_concepto(concepto)

        return concepto.to_dict(),200

    except Exception as e:
        return {"error": f"Error al eliminar keyword del concepto: {str(e)}"},500

# Devuelve los conceptos asociados a un área
@api_conceptos.route('/conceptos/area', methods=['GET'])
@SerializeJson
def get_conceptos_in_area():
    try:
        area_id = request.args.get("area_id")
        if not area_id or not ObjectId.is_valid(area_id):
            return {"error": "ID de área no válido"},400

        conceptos = get_conceptos_by_area_id(ObjectId(area_id))
        return conceptos,200

    except Exception as e:
        return {"error": f"Error al obtener conceptos: {str(e)}"},500
