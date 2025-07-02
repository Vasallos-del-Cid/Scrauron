from flask import Blueprint, request, jsonify

from ..models.modelUtils.SerializeJson import SerializeJson
from ..mongo.mongo_keywords import (
    get_keywords, 
    get_keyword_by_id,create_keyword, 
    delete_keyword, update_keyword,
    get_keywords_by_concepto_id,
    get_collection
    )
from ..models.keyword import Keyword
from bson import ObjectId

api_keywords = Blueprint('api_keywords', __name__)

# -----------------------------------------------
# GET todas las keywords
@api_keywords.route('/keywords', methods=['GET'])
@SerializeJson
def get_keywords_endpoint():
    try:
        keywords = get_keywords()
        return keywords, 200
    except Exception as e:
        return {"error": str(e)}, 500

# -----------------------------------------------
# GET una keyword por ID
@api_keywords.route('/keywords/<keyword_id>', methods=['GET'])
@SerializeJson
def get_keyword_endpoint(keyword_id):
    try:
        keyword = get_keyword_by_id(keyword_id)
        if not keyword:
            return {"error": "Keyword no encontrada"}, 404
        return keyword.to_dict(), 200
    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

# -----------------------------------------------
# POST nueva keyword
@api_keywords.route('/keywords', methods=['POST'])
@SerializeJson
def create_keyword_endpoint():
    try:
        keyword = Keyword.from_dict(request.get_json())
        body, status = create_keyword(keyword)  
        return body, status                     
    except Exception as e:
        return {"error": str(e)}, 400

# -----------------------------------------------
# DELETE una keyword por ID
@api_keywords.route('/keywords/<keyword_id>', methods=['DELETE'])
@SerializeJson
def delete_keyword_endpoint(keyword_id):
    try:
        deleted_count = delete_keyword(keyword_id)
        if deleted_count == 0:
            return {"error": "Keyword no encontrada"}, 404
        return "", 204
    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

# -----------------------------------------------
# PATCH actualizar una keyword
@api_keywords.route('/keywords/<keyword_id>', methods=['PATCH'])
@SerializeJson
def patch_keyword_endpoint(keyword_id):
    data = request.get_json()
    try:
        updated_keyword = update_keyword(keyword_id, data)

        if not updated_keyword:
            return {"error": "Keyword no encontrada"}, 404

        return updated_keyword, 200

    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

# -----------------------------------------------
# GET keywords de un concepto
@api_keywords.route('/keywords/concepto', methods=['GET'])
@SerializeJson
def get_keywords_by_concepto_route():
    try:
        concepto_id = request.args.get("concepto_id")
        if not concepto_id or not ObjectId.is_valid(concepto_id):
            return {"error": "ID de concepto no válido."}, 400

        keywords_ids = get_keywords_by_concepto_id(ObjectId(concepto_id))
        return keywords_ids, 200

    except Exception as e:
        return {"error": f"Error al obtener keywords: {str(e)}"}, 500


# -----------------------------------------------
# GET keywords relacionadas de una publicacion
@api_keywords.route('/keywords/publicacion', methods=['GET'])
@SerializeJson
def get_keywords_by_publicacion_route():
    try:
        publicacion_id = request.args.get("publicacion_id")
        if not publicacion_id or not ObjectId.is_valid(publicacion_id):
            return {"error": "ID de publicación no válido o ausente"}, 400

        pub_oid = ObjectId(publicacion_id)
        publicacion = get_collection("publicaciones").find_one({"_id": pub_oid})
        if not publicacion:
            return {"error": "Publicación no encontrada"}, 404

        keyword_ids = publicacion.get("keywords_relacionadas_ids", [])
        if not keyword_ids:
            return [], 200

        keywords = get_collection("keywords").find({"_id": {"$in": keyword_ids}})

        if not keywords:
            resultado = []
        else:
            resultado = [Keyword.from_dict(keyword).to_dict() for keyword in keywords]

        return resultado, 200

    except Exception as e:
        return {"error": f"Error al obtener keywords: {str(e)}"}, 500
