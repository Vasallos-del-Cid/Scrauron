from flask import Blueprint, request, jsonify
from ..models.concepto_interes import ConceptoInteres
from ..mongo.mongo_conceptos import (
    get_conceptos,
    get_concepto_by_id,
    create_concepto,
    update_concepto,
    delete_concepto
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
        conceptos = [_convert_objectid(c) for c in conceptos]
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


