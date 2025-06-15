from flask import Blueprint, request, jsonify

from ..models.modelUtils.SerializeJson import SerializeJson
from ..models.publicacion import Publicacion
from ..mongo.mongo_publicaciones import (
    get_publicaciones,
    get_publicacion_by_id,
    create_publicacion,
    update_publicacion,
    delete_publicacion,
    delete_all_publicaciones, get_publicaciones_con_conceptos
)

api_publicaciones = Blueprint('api_publicaciones', __name__)

# GET todas las publicaciones
@api_publicaciones.route('/publicaciones', methods=['GET'])
@SerializeJson
def get_publicaciones_endpoint():
    try:
        publicaciones = get_publicaciones()
        return publicaciones, 200
    except Exception as e:
        return {"error": f"Error al obtener publicaciones: {str(e)}"}, 500

# GET una publicación por ID
@api_publicaciones.route('/publicaciones/<pub_id>', methods=['GET'])
@SerializeJson
def get_publicacion_endpoint(pub_id):
    try:
        publicacion = get_publicacion_by_id(pub_id)
        if not publicacion:
            return {"error": "Publicación no encontrada"}, 404
        return publicacion, 200
    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}, 500

# POST crear publicación
@api_publicaciones.route('/publicaciones', methods=['POST'])
@SerializeJson
def create_publicacion_endpoint():
    try:
        data = request.get_json()
        publicacion = Publicacion.from_dict(data)

        # Asegurar que no haya un _id manual que cause conflicto
        pub_dict = publicacion.to_dict()
        if "_id" in pub_dict and pub_dict["_id"] is None:
            del pub_dict["_id"]

        insert_result = create_publicacion(publicacion)

        if insert_result is None or not hasattr(insert_result, "inserted_id"):
            return {"error": "Error al insertar la publicación en la base de datos"}, 500

        publicacion._id = str(insert_result.inserted_id)
        return publicacion.to_dict(), 201

    except ValueError as ve:
        return {"error": f"Datos inválidos: {str(ve)}"}, 400
    except Exception as e:
        return {"error": f"Error al crear publicación: {str(e)}"}, 500

# PATCH actualizar publicación parcial
@api_publicaciones.route('/publicaciones/<pub_id>', methods=['PATCH'])
@SerializeJson
def patch_publicacion_endpoint(pub_id):
    try:
        data = request.get_json()
        updated = update_publicacion(pub_id, data)
        if not updated:
            return {"error": "Publicación no encontrada"}, 404
        return updated, 200
    except ValueError as ve:
        return {"error": f"ID inválido: {str(ve)}"}, 400
    except Exception as e:
        return {"error": f"Error al actualizar publicación: {str(e)}"}, 500

# DELETE eliminar publicación
@api_publicaciones.route('/publicaciones/<pub_id>', methods=['DELETE'])
@SerializeJson
def delete_publicacion_endpoint(pub_id):
    try:
        deleted_count = delete_publicacion(pub_id)
        if deleted_count == 0:
            return {"error": "Publicación no encontrada"}, 404
        return '', 204
    except ValueError as ve:
        return {"error": f"ID inválido: {str(ve)}"}, 400
    except Exception as e:
        return {"error": f"Error al eliminar publicación: {str(e)}"}, 500

@api_publicaciones.route('/publicaciones', methods=['DELETE'])
@SerializeJson
def delete_all_publicaciones_endpoint():
    try:
        count = delete_all_publicaciones()
        return {"mensaje": f"Se eliminaron {count} publicaciones"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

# GET una publicación por ID
@api_publicaciones.route('/publicacionesconceptos', methods=['GET'])
@SerializeJson
def publicaciones_con_conceptos():
    try:
        publicaciones = get_publicaciones_con_conceptos()
        return publicaciones, 200
    except Exception as e:
        return {"error": f"Error al obtener publicaciones: {str(e)}"}, 500