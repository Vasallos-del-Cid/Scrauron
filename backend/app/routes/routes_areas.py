from flask import Blueprint, request, jsonify
from ..models.area_de_trabajo import AreaDeTrabajo
from ..mongo.mongo_areas import (
    get_areas,
    get_area_by_id,
    create_area,
    update_area,
    delete_area
)

api_areas = Blueprint('api_areas', __name__)

@api_areas.route('/areas', methods=['GET'])
def get_areas_endpoint():
    try:
        return jsonify(get_areas()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_areas.route('/areas/<area_id>', methods=['GET'])
def get_area_endpoint(area_id):
    try:
        area = get_area_by_id(area_id)
        if not area:
            return jsonify({"error": "Área no encontrada"}), 404
        return jsonify(area), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

@api_areas.route('/areas', methods=['POST'])
def create_area_endpoint():
    data = request.get_json()
    try:
        area = AreaDeTrabajo.from_dict(data)
        insert_result = create_area(area)
        area._id = str(insert_result.inserted_id)
        return jsonify(area.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_areas.route('/areas/<area_id>', methods=['PATCH'])
def patch_area_endpoint(area_id):
    data = request.get_json()
    try:
        updated = update_area(area_id, data)
        if not updated:
            return jsonify({"error": "Área no encontrada"}), 404
        return jsonify(updated), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

@api_areas.route('/areas/<area_id>', methods=['DELETE'])
def delete_area_endpoint(area_id):
    try:
        deleted = delete_area(area_id)
        if deleted == 0:
            return jsonify({"error": "Área no encontrada"}), 404
        return '', 204
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
