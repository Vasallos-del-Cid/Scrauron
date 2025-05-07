from flask import Blueprint, request, jsonify
from ..models.area_de_trabajo import AreaDeTrabajo
from ..mongo.mongo_areas import (
    get_areas,
    get_area_by_id,
    create_area,
    update_area,
    delete_area,
    agregar_concepto_a_area,
    agregar_fuente_a_area
)

api_areas = Blueprint('api_areas', __name__)

# GET todas las áreas
@api_areas.route('/areas', methods=['GET'])
def get_areas_endpoint():
    try:
        areas = get_areas()
        areas_dicts = [area.to_dict() for area in areas]
        return jsonify(areas_dicts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET área por ID
@api_areas.route('/areas/<area_id>', methods=['GET'])
def get_area_endpoint(area_id):
    try:
        area_dict = get_area_by_id(area_id)
        if not area_dict:
            return jsonify({"error": "Área no encontrada"}), 404
        area = AreaDeTrabajo.from_dict(area_dict)
        return jsonify(area.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST crear nueva área
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

# PATCH actualizar campos de un área (parcial)
@api_areas.route('/areas/<area_id>', methods=['PATCH'])
def patch_area_endpoint(area_id):
    data = request.get_json()
    try:
        area_dict = get_area_by_id(area_id)
        if not area_dict:
            return jsonify({"error": "Área no encontrada"}), 404
        area = AreaDeTrabajo.from_dict(area_dict)

        # aplicar cambios desde el request
        if 'nombre' in data:
            area.nombre = data['nombre']

        update_area(area)
        return jsonify(area.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# DELETE eliminar área
@api_areas.route('/areas/<area_id>', methods=['DELETE'])
def delete_area_endpoint(area_id):
    try:
        deleted = delete_area(area_id)
        if deleted == 0:
            return jsonify({"error": "Área no encontrada"}), 404
        return '', 204
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

# PATCH agregar un concepto a un área
@api_areas.route('/areas/<area_id>/agregar_concepto', methods=['PATCH'])
def agregar_concepto_endpoint(area_id):
    data = request.get_json()
    concepto_id = data.get("concepto_id")
    if not concepto_id:
        return jsonify({"error": "Falta 'concepto_id'"}), 400
    try:
        ok = agregar_concepto_a_area(area_id, concepto_id)
        if not ok:
            return jsonify({"message": "El concepto ya estaba asociado"}), 200
        return jsonify({"message": "Concepto agregado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# PATCH agregar una fuente a un área
@api_areas.route('/areas/<area_id>/agregar_fuente', methods=['PATCH'])
def agregar_fuente_endpoint(area_id):
    data = request.get_json()
    fuente_id = data.get("fuente_id")
    if not fuente_id:
        return jsonify({"error": "Falta 'fuente_id'"}), 400
    try:
        ok = agregar_fuente_a_area(area_id, fuente_id)
        if not ok:
            return jsonify({"message": "La fuente ya estaba asociada"}), 200
        return jsonify({"message": "Fuente agregada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
