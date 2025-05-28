from flask import Blueprint, request, jsonify
from ..models.concepto_interes import ConceptoInteres
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
    if "publicaciones_relacionadas_ids" in doc:
        doc["publicaciones_relacionadas_ids"] = [str(pid) for pid in doc["publicaciones_relacionadas_ids"]]
    return doc

@api_conceptos.route('/conceptos', methods=['GET'])
def get_conceptos_endpoint():
    try:
        conceptos = get_conceptos()
        return jsonify(conceptos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_conceptos.route('/conceptos/<concepto_id>', methods=['GET'])
def get_concepto_endpoint(concepto_id):
    try:
        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return jsonify({"error": "Concepto no encontrado"}), 404
        return jsonify(_convert_objectid(concepto.to_dict())), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

@api_conceptos.route('/conceptos', methods=['POST'])
def create_concepto_endpoint():
    data = request.get_json()
    try:
        concepto = ConceptoInteres.from_dict(data)
        insert_result = create_concepto(concepto)

        if insert_result is None or not hasattr(insert_result, "inserted_id"):
            return jsonify({"error": "Error al insertar el concepto"}), 500

        concepto._id = str(insert_result.inserted_id)
        return jsonify(_convert_objectid(concepto.to_dict())), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_conceptos.route('/conceptos/<concepto_id>', methods=['PATCH'])
def patch_concepto_endpoint(concepto_id):
    data = request.get_json()
    try:
        concepto = ConceptoInteres.from_dict(data)
        concepto._id = concepto_id
        update_concepto(concepto)
        return jsonify(_convert_objectid(concepto.to_dict())), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_conceptos.route('/conceptos/<concepto_id>', methods=['DELETE'])
def delete_concepto_endpoint(concepto_id):
    try:
        deleted = delete_concepto(concepto_id)
        if deleted == 0:
            return jsonify({"error": "Concepto no encontrado"}), 404
        return '', 204
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

# PATCH /conceptos/<id>/generar_descripcion → Genera descripción y devuelve el concepto actualizado
@api_conceptos.route('/conceptos/<concepto_id>/generar_descripcion', methods=['PATCH'])
def generar_descripcion_concepto(concepto_id):
    concepto = get_concepto_by_id(concepto_id)
    if not concepto:
        return jsonify({"error": "Concepto no encontrado"}), 404

    add_descripcion_llm(concepto)

    return jsonify(concepto.to_dict()), 200

# PATCH /conceptos/<id>/generar_keywords → Actualiza descripción y genera keywords
@api_conceptos.route('/conceptos/<concepto_id>/generar_keywords', methods=['PATCH'])
def generar_keywords_concepto(concepto_id):
    try:
        data = request.get_json()
        nueva_descripcion = data.get("descripcion")

        if not nueva_descripcion:
            return jsonify({"error": "Debe proporcionarse una descripción para generar keywords"}), 400

        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return jsonify({"error": "Concepto no encontrado"}), 404

        # Actualizar la descripción recibida
        concepto.descripcion = nueva_descripcion

        # Generar keywords con el LLM y actualizar el concepto
        add_keywords_llm(concepto)

        return jsonify(concepto.to_dict()), 200

    except Exception as e:
        return jsonify({"error": f"Error al generar keywords para el concepto: {str(e)}"}), 500

# PATCH /conceptos/<id>/keywords_aceptadas → Actualiza keywords y agrega concepto a area
@api_conceptos.route('/conceptos/<area_id>/keywords_aceptadas', methods=['PATCH'])
def update_keywords_ids_en_area_endpoint(area_id):
    try:
        if not ObjectId.is_valid(area_id):
            return jsonify({"error": "ID de área no válido."}), 400

        data = request.get_json()
        # Obtener y validar el objeto concepto
        concepto_id = data.get("_id")
        if not concepto_id:
            return jsonify({"error": "El concepto debe contener _id."}), 400

        if not ObjectId.is_valid(concepto_id):
            return jsonify({"error": f"ID de concepto no válido: {concepto_id}"}), 400

        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return jsonify({"error": "Concepto no encontrado"}), 404

        # Obtener y validar keywords_ids
        keywords_ids_raw = data.get("keywords_ids", [])
        if not isinstance(keywords_ids_raw, list):
            return jsonify({"error": "keywords_ids debe ser una lista."}), 400

        keywords_ids = []
        for kid in keywords_ids_raw:
            if not ObjectId.is_valid(str(kid)):
                return jsonify({"error": f"ID de keyword no válido: {kid}"}), 400
            keywords_ids.append(ObjectId(str(kid)))

        # Actualiza el concepto
        concepto.keywords_ids = keywords_ids
        update_concepto(concepto)

        # Agrega el concepto al área usando tu función
        agregar_concepto_a_area(area_id, concepto._id)

        return jsonify(concepto.to_dict()), 200

    except Exception as e:
        return jsonify({"error": f"Error al actualizar keywords y vincular área: {str(e)}"}), 500


    except Exception as e:
        return jsonify({"error": f"Error al actualizar keywords y vincular área: {str(e)}"}), 500

    
    # Agrega una keyword al concepto (si no está ya)
@api_conceptos.route('/conceptos/<concepto_id>/keywords', methods=['POST'])
def add_keyword_to_concepto(concepto_id):
    try:
        data = request.get_json()
        keyword_id = data.get("keyword_id")

        if not keyword_id or not ObjectId.is_valid(keyword_id):
            return jsonify({"error": "keyword_id no válido"}), 400

        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return jsonify({"error": "Concepto no encontrado"}), 404

        keyword_oid = ObjectId(keyword_id)

        if keyword_oid not in concepto.keywords_ids:
            concepto.keywords_ids.append(keyword_oid)
            update_concepto(concepto)

        return jsonify(concepto.to_dict()), 200

    except Exception as e:
        return jsonify({"error": f"Error al agregar keyword al concepto: {str(e)}"}), 500

# ---------------------------------------------------
# Elimina una keyword del concepto
@api_conceptos.route('/conceptos/<concepto_id>/keywords/<keyword_id>', methods=['DELETE'])
def remove_keyword_from_concepto(concepto_id, keyword_id):
    try:
        if not ObjectId.is_valid(keyword_id):
            return jsonify({"error": "keyword_id no válido"}), 400

        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return jsonify({"error": "Concepto no encontrado"}), 404

        keyword_oid = ObjectId(keyword_id)

        if keyword_oid in concepto.keywords_ids:
            concepto.keywords_ids.remove(keyword_oid)
            update_concepto(concepto)

        return jsonify(concepto.to_dict()), 200

    except Exception as e:
        return jsonify({"error": f"Error al eliminar keyword del concepto: {str(e)}"}), 500

# ---------------------------------------------------
# Da los conceptos de un area

@api_conceptos.route('/conceptos/area', methods=['GET'])
def get_conceptos_in_area():
    try:
        area_id = request.args.get("area_id")
        if not area_id or not ObjectId.is_valid(area_id):
            return jsonify({"error": "ID de área no válido"}), 400

        conceptos = get_conceptos_id_by_area_id(ObjectId(area_id))
        return jsonify(conceptos), 200

    except Exception as e:
        return jsonify({"error": f"Error al obtener conceptos: {str(e)}"}), 500

