from flask import Blueprint, request, jsonify
from ..models.publicacion import Publicacion
from ..mongo.mongo_publicaciones import (
    get_publicaciones,
    get_publicacion_by_id,
    create_publicacion,
    update_publicacion,
    delete_publicacion
)

api_publicaciones = Blueprint('api_publicaciones', __name__)

@api_publicaciones.route('/publicaciones', methods=['GET'])
def get_publicaciones_endpoint():
    try:
        return jsonify(get_publicaciones()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_publicaciones.route('/publicaciones/<pub_id>', methods=['GET'])
def get_publicacion_endpoint(pub_id):
    try:
        pub = get_publicacion_by_id(pub_id)
        if not pub:
            return jsonify({"error": "Publicación no encontrada"}), 404
        return jsonify(pub), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

@api_publicaciones.route('/publicaciones', methods=['POST'])
def create_publicacion_endpoint():
    data = request.get_json()
    try:
        publicacion = Publicacion.from_dict(data)
        insert_result = create_publicacion(publicacion)
        publicacion._id = str(insert_result.inserted_id)
        return jsonify(publicacion.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_publicaciones.route('/publicaciones/<pub_id>', methods=['PATCH'])
def patch_publicacion_endpoint(pub_id):
    data = request.get_json()
    try:
        updated = update_publicacion(pub_id, data)
        if not updated:
            return jsonify({"error": "Publicación no encontrada"}), 404
        return jsonify(updated), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

@api_publicaciones.route('/publicaciones/<pub_id>', methods=['DELETE'])
def delete_publicacion_endpoint(pub_id):
    try:
        deleted = delete_publicacion(pub_id)
        if deleted == 0:
            return jsonify({"error": "Publicación no encontrada"}), 404
        return '', 204
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
