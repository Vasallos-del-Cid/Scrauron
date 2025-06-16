from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from ..models.modelUtils.SerializeJson import SerializeJson
from ..models.publicacion import Publicacion
from ..mongo.mongo_publicaciones import (
    get_publicaciones,
    get_publicacion_by_id,
    create_publicacion,
    update_publicacion,
    delete_publicacion,
    delete_all_publicaciones,
    get_publicaciones_con_conceptos,
    filtrar_publicaciones
)
from ..mongo.mongo_fuentes import get_fuente_by_id, get_collection, get_fuentes_dict
from ..mongo.mongo_conceptos import get_collection as get_conceptos_collection

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

@api_publicaciones.route('/publicacionesconceptos', methods=['GET'])
@SerializeJson
def publicaciones_con_conceptos():
    try:
        publicaciones = get_publicaciones_con_conceptos()
        return publicaciones, 200
    except Exception as e:
        return {"error": f"Error al obtener publicaciones: {str(e)}"}, 500

@api_publicaciones.route('/publicaciones_filtradas', methods=['GET'])
@SerializeJson
def publicaciones_filtradas_endpoint():
    try:
        fecha_inicio_str = request.args.get("fechaInicio")
        fecha_fin_str = request.args.get("fechaFin")
        concepto_id_str = request.args.get("concepto_interes")
        area_id_str = request.args.get("area_id")
        fuente_id_str = request.args.get("fuente_id")
        tono_str = request.args.get("tono")
        keywords_str = request.args.getlist("keywordsRelacionadas")
        busqueda_palabras = request.args.get("busqueda_palabras")

        if not fecha_inicio_str or not fecha_fin_str:
            return {"error": "Los parámetros fechaInicio y fechaFin son obligatorios"}, 400

        fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
        fecha_fin = datetime.fromisoformat(fecha_fin_str)

        concepto_id = ObjectId(concepto_id_str) if concepto_id_str else None
        area_id = ObjectId(area_id_str) if area_id_str else None
        fuente_id = ObjectId(fuente_id_str) if fuente_id_str else None
        tono = int(tono_str) if tono_str else None
        keywords = [ObjectId(k) for k in keywords_str] if keywords_str else None

        publicaciones = filtrar_publicaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            concepto_interes=concepto_id,
            tono=tono,
            keywords_relacionadas=keywords,
            busqueda_palabras=busqueda_palabras,
            area_id=area_id,
            fuente_id=fuente_id
        )

        # --- Obtener fuentes y convertir _id a str para coincidencia
        fuentes_dict = {str(f["_id"]): f for f in get_fuentes_dict()}

        # --- Obtener conceptos de Mongo
        all_concept_ids = set()
        for pub in publicaciones:
            for cid in pub.get("conceptos_relacionados_ids", []):
                all_concept_ids.add(cid)
        conceptos_cursor = get_conceptos_collection("conceptos_interes").find({"_id": {"$in": list(all_concept_ids)}})
        conceptos_dict = {str(c["_id"]): c for c in conceptos_cursor}

        # --- Asignar objetos completos a cada publicación
        for pub in publicaciones:
            f_id = str(pub.get("fuente_id"))
            pub["fuente"] = fuentes_dict.get(f_id)

            cr_ids = [str(cid) for cid in pub.get("conceptos_relacionados_ids", [])]
            pub["conceptos_relacionados"] = [
                conceptos_dict[cid] for cid in cr_ids if cid in conceptos_dict
            ]
            pub.pop("conceptos_relacionados_ids", None)

        return publicaciones, 200

    except ValueError as ve:
        return {"error": f"Parámetro inválido: {str(ve)}"}, 400
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}, 500
