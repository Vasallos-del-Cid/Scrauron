from flask import Blueprint, request, jsonify
from ..mongo.mongo_fuentes import get_fuentes, create_fuente, delete_fuente, update_fuente, get_fuente_by_id
from ..models.fuente import Fuente
from bson import ObjectId

api_fuentes = Blueprint('api_fuentes', __name__)

#Endpoints fuentes

#GET Fuentes
@api_fuentes.route('/fuentes', methods=['GET'])
def get_fuentes_endpoint():
    try:
        fuentes = get_fuentes()
        return jsonify(fuentes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#GET Fuente
@api_fuentes.route('/fuentes/<fuente_id>', methods=['GET'])
def get_fuente_endpoint(fuente_id):
    try:
        fuente = get_fuente_by_id(fuente_id)
        if not fuente:
            return jsonify({"error": "Fuente no encontrada"}), 404
        return jsonify(fuente.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST nueva fuente
@api_fuentes.route('/fuentes', methods=['POST'])
def create_fuente_endpoint():
    data = request.get_json()
    try:
        fuente = Fuente.from_dict(data)
        response, status_code = create_fuente(fuente)

        if status_code == 201:
            json_data = response.get_json()
            fuente._id = json_data["_id"]
            return response
        else:
            return response, status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Eliminar fuente
@api_fuentes.route('/fuentes/<fuente_id>', methods=['DELETE'])
def delete_fuente_endpoint(fuente_id):
    try:
        deleted_count = delete_fuente(fuente_id)
        if deleted_count == 0:
            return jsonify({"error": "Fuente no encontrada"}), 404
        return '', 204
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Actualizar fuente
@api_fuentes.route('/fuentes/<fuente_id>', methods=['PATCH'])
def patch_fuente_endpoint(fuente_id):
    data = request.get_json()
    try:
        updated_fuente = update_fuente(fuente_id, data)

        if not updated_fuente:
            return jsonify({"error": "Fuente no encontrada"}), 404

        return jsonify(updated_fuente), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500