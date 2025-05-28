from flask import Blueprint, request, jsonify
from ..mongo.mongo_keywords import (
    get_keywords, 
    get_keyword_by_id,create_keyword, 
    delete_keyword, update_keyword,
    get_keywords_id_by_concepto_id,
    get_collection
    )
from ..models.keyword import Keyword
from bson import ObjectId

api_keywords = Blueprint('api_keywords', __name__)

# -----------------------------------------------
# GET todas las keywords
@api_keywords.route('/keywords', methods=['GET'])
def get_keywords_endpoint():
    try:
        keywords = get_keywords()
        return jsonify(keywords), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------
# GET una keyword por ID
@api_keywords.route('/keywords/<keyword_id>', methods=['GET'])
def get_keyword_endpoint(keyword_id):
    try:
        keyword = get_keyword_by_id(keyword_id)
        if not keyword:
            return jsonify({"error": "Keyword no encontrada"}), 404
        return jsonify(keyword.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------
# POST nueva keyword
@api_keywords.route('/keywords', methods=['POST'])
def create_keyword_endpoint():
    data = request.get_json()
    try:
        keyword = Keyword.from_dict(data)
        response, status_code = create_keyword(keyword)

        if status_code == 201:
            json_data = response.get_json()
            keyword._id = json_data["_id"]
            return response
        else:
            return response, status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# -----------------------------------------------
# DELETE una keyword por ID
@api_keywords.route('/keywords/<keyword_id>', methods=['DELETE'])
def delete_keyword_endpoint(keyword_id):
    try:
        deleted_count = delete_keyword(keyword_id)
        if deleted_count == 0:
            return jsonify({"error": "Keyword no encontrada"}), 404
        return '', 204
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------
# PATCH actualizar una keyword
@api_keywords.route('/keywords/<keyword_id>', methods=['PATCH'])
def patch_keyword_endpoint(keyword_id):
    data = request.get_json()
    try:
        updated_keyword = update_keyword(keyword_id, data)

        if not updated_keyword:
            return jsonify({"error": "Keyword no encontrada"}), 404

        return jsonify(updated_keyword), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------
# GET keywords de un concepto
@api_keywords.route('/keywords/concepto', methods=['GET'])
def get_keywords_by_concepto_route():
    try:
        concepto_id = request.args.get("concepto_id")
        if not concepto_id or not ObjectId.is_valid(concepto_id):
            return jsonify({"error": "ID de concepto no válido."}), 400

        keywords_ids = get_keywords_id_by_concepto_id(ObjectId(concepto_id))
        return jsonify(keywords_ids), 200

    except Exception as e:
        return jsonify({"error": f"Error al obtener keywords: {str(e)}"}), 500


# -----------------------------------------------
# GET keywords relacionadas de una publicacion
@api_keywords.route('/keywords/publicacion', methods=['GET'])
def get_keywords_relacionadas_by_publicacion():
    try:
        publicacion_id = request.args.get("publicacion_id")
        if not publicacion_id or not ObjectId.is_valid(publicacion_id):
            return jsonify({"error": "ID de publicación no válido."}), 400

        publicacion = get_collection('publicaciones').find_one({"_id": ObjectId(publicacion_id)})
        if not publicacion:
            return jsonify({"error": "Publicación no encontrada"}), 404

        keywords_oids = publicacion.get("keywords_relacionadas_ids", [])
        if not keywords_oids:
            return [], 200
        
        keywords_ids = []
        for keyword_oid in keywords_oids:
            keywords_ids.append(str(keyword_oid))

        return keywords_ids, 200

    except Exception as e:
        return jsonify({"error": f"Error al obtener keywords relacionadas: {str(e)}"}), 500
