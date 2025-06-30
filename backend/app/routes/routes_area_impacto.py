from flask import Blueprint, request, jsonify
from ..models.area_impacto import AreaImpacto
from ..models.modelUtils.SerializeJson import SerializeJson
from ..mongo.mongo_area_impacto import (
    get_areas_impacto,
    get_area_impacto_by_id,
    create_area_impacto,
    update_area_impacto,
    delete_area_impacto
)

api_areas_impacto = Blueprint('api_areas_impacto', __name__)

# GET todas las áreas de impacto
@api_areas_impacto.route('/areas_impacto', methods=['GET'])
@SerializeJson
def get_areas_impacto_endpoint():
    try:
        areas = get_areas_impacto()
        return [area.to_dict() for area in areas], 200
    except Exception as e:
        return {"error": str(e)}, 500

# GET área de impacto por ID
@api_areas_impacto.route('/areas_impacto/<area_id>', methods=['GET'])
def get_area_impacto_endpoint(area_id):
    try:
        area_dict = get_area_impacto_by_id(area_id)
        if not area_dict:
            return {"error": "Área de impacto no encontrada"}, 404
        area = AreaImpacto.from_dict(area_dict)
        return area.to_dict(), 200
    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

# POST crear nueva área de impacto
@api_areas_impacto.route('/areas_impacto', methods=['POST'])
def create_area_impacto_endpoint():
    data = request.get_json()
    try:
        area = AreaImpacto.from_dict(data)
        insert_result = create_area_impacto(area)
        area._id = str(insert_result.inserted_id)
        return area.to_dict(), 201
    except Exception as e:
        return {"error": str(e)}, 400

# PATCH actualizar campos de un área de impacto
@api_areas_impacto.route('/areas_impacto/<area_id>', methods=['PATCH'])
def patch_area_impacto_endpoint(area_id):
    data = request.get_json()
    try:
        area_dict = get_area_impacto_by_id(area_id)
        if not area_dict:
            return {"error": "Área de impacto no encontrada"}, 404
        area = AreaImpacto.from_dict(area_dict)

        if 'nombre' in data:
            area.nombre = data['nombre']
        if 'descripcion' in data:
            area.descripcion = data['descripcion']
        if 'area_id' in data:
            area.area_id = data['area_id']

        update_area_impacto(area)
        return area.to_dict(), 200
    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

# DELETE eliminar área de impacto
@api_areas_impacto.route('/areas_impacto/<area_id>', methods=['DELETE'])
def delete_area_impacto_endpoint(area_id):
    try:
        deleted = delete_area_impacto(area_id)
        if deleted == 0:
            return {"error": "Área de impacto no encontrada"}, 404
        return '', 204
    except ValueError as ve:
        return {"error": str(ve)}, 400

# GET áreas de impacto por area_id
@api_areas_impacto.route('/areas_impacto/por_area/<area_id>', methods=['GET'])
@SerializeJson
def get_areas_impacto_por_area_id_endpoint(area_id):
    try:
        todas = get_areas_impacto()
        filtradas = [a.to_dict() for a in todas if a.area_id == area_id]
        return filtradas, 200
    except Exception as e:
        return {"error": str(e)}, 500
