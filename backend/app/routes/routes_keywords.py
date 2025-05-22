from flask import Blueprint, request, jsonify
from ..mongo.mongo_keywords import (
    get_keywords, get_keyword_by_id, get_keyword_by_nombre,
    create_keyword, delete_keyword, update_keyword
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
