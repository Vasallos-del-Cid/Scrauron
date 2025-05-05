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

@api_conceptos.route('/conceptos', methods=['GET'])
def get_conceptos_endpoint():
    try:
        return jsonify(get_conceptos()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_conceptos.route('/conceptos/<concepto_id>', methods=['GET'])
def get_concepto_endpoint(concepto_id):
    try:
        concepto = get_concepto_by_id(concepto_id)
        if not concepto:
            return jsonify({"error": "Concepto no encontrado"}), 404
        return jsonify(concepto), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

@api_conceptos.route('/conceptos', methods=['POST'])
def create_concepto_endpoint():
    data = request.get_json()
    try:
        concepto = ConceptoInteres.from_dict(data)
        insert_result = create_concepto(concepto)
        concepto._id = str(insert_result.inserted_id)
        return jsonify(concepto.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_conceptos.route('/conceptos/<concepto_id>', methods=['PATCH'])
def patch_concepto_endpoint(concepto_id):
    data = request.get_json()
    try:
        updated = update_concepto(concepto_id, data)
        if not updated:
            return jsonify({"error": "Concepto no encontrado"}), 404
        return jsonify(updated), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

@api_conceptos.route('/conceptos/<concepto_id>', methods=['DELETE'])
def delete_concepto_endpoint(concepto_id):
    try:
        deleted = delete_concepto(concepto_id)
        if deleted == 0:
            return jsonify({"error": "Concepto no encontrado"}), 404
        return '', 204
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
