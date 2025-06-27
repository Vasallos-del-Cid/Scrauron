from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from bson import ObjectId
import logging
from collections import defaultdict
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
    filtrar_publicaciones,
    eliminar_concepto_de_publicacion
)
from ..mongo.mongo_fuentes import  get_fuentes_dict
from ..mongo.mongo_conceptos import get_collection as get_conceptos_collection
from ..service.llm.llm_utils import generar_informe_impacto_temporal

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
        # Parámetros
        fi = request.args.get("fechaInicio")
        ff = request.args.get("fechaFin")
        ci = request.args.get("concepto_interes")
        ai = request.args.get("area_id")
        fiu = request.args.get("fuente_id")
        tone = request.args.get("tono")
        kws = request.args.getlist("keywordsRelacionadas")
        busq = request.args.get("busqueda_palabras")
        pais = request.args.get("pais")  
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("pageSize", 25))

        if not fi or not ff:
            return {"error": "Los parámetros fechaInicio y fechaFin son obligatorios"}, 400

        fecha_inicio = datetime.fromisoformat(fi)
        fecha_fin = datetime.fromisoformat(ff)

        concepto_oid = ObjectId(ci) if ci else None
        area_id = ObjectId(ai) if ai else None
        fuente_id = ObjectId(fiu) if fiu else None
        tono = int(tone) if tone else None
        keywords = [ObjectId(k) for k in kws] if kws else None

        publicaciones = filtrar_publicaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tono=tono,
            keywords_relacionadas=keywords,
            busqueda_palabras=busq,
            area_id=area_id,
            fuente_id=fuente_id,
            pais=pais  
        )

        if concepto_oid:
            publicaciones = [
                pub for pub in publicaciones
                if concepto_oid in pub.get("conceptos_relacionados_ids", [])
            ]

        total = len(publicaciones)
        inicio = (page - 1) * page_size
        fin = inicio + page_size
        publicaciones = publicaciones[inicio:fin]

        # --- Obtener fuentes y conceptos completos
        fuentes_map = {str(f["_id"]): f for f in get_fuentes_dict()}
        all_concepts = set()
        for pub in publicaciones:
            all_concepts.update(pub.get("conceptos_relacionados_ids", []))
        conceptos_map = {
            str(c["_id"]): c
            for c in get_conceptos_collection("conceptos_interes").find(
                {"_id": {"$in": list(all_concepts)}}
            )
        }

        # Enriquecer publicaciones con objetos fuente y conceptos
        for pub in publicaciones:
            f_id = str(pub.get("fuente_id"))
            pub["fuente"] = fuentes_map.get(f_id)

            cr_ids = [str(cid) for cid in pub.get("conceptos_relacionados_ids", [])]
            pub["conceptos_relacionados"] = [conceptos_map[cid] for cid in cr_ids if cid in conceptos_map]
            pub.pop("conceptos_relacionados_ids", None)

        return {"total": total, "publicaciones": publicaciones}, 200

    except ValueError as ve:
        return {"error": f"Parámetro inválido: {ve}"}, 400
    except Exception as e:
        return {"error": f"Error inesperado: {e}"}, 500



@api_publicaciones.route('/publicaciones/<pub_id>/conceptos/<concepto_id>', methods=['DELETE'])
@SerializeJson
def eliminar_concepto_relacionado_endpoint(pub_id, concepto_id):
    try:
        count = eliminar_concepto_de_publicacion(pub_id, concepto_id)
        if count == 0:
            return {"mensaje": "No se encontró la publicación o el concepto no estaba relacionado"}, 404
        return {"mensaje": "Concepto eliminado de la publicación"}, 200
    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": f"Error al eliminar el concepto: {str(e)}"}, 500


@api_publicaciones.route('/informe_impacto_temporal', methods=['GET'])
def informe_impacto_temporal_endpoint():
    try:
        fi = request.args.get("fechaInicio")
        ff = request.args.get("fechaFin")
        ci = request.args.get("concepto_interes")
        ai = request.args.get("area_id")
        fiu = request.args.get("fuente_id")
        tone = request.args.get("tono")
        kws = request.args.getlist("keywordsRelacionadas")
        busq = request.args.get("busqueda_palabras")
        pais = request.args.get("pais")

        if not fi or not ff:
            return {"error": "Los parámetros fechaInicio y fechaFin son obligatorios"}, 400

        fecha_inicio = datetime.fromisoformat(fi)
        fecha_fin = datetime.fromisoformat(ff)

        concepto_oid = ObjectId(ci) if ci else None
        area_id = ObjectId(ai) if ai else None
        fuente_id = ObjectId(fiu) if fiu else None
        tono = int(tone) if tone else None
        keywords = [ObjectId(k) for k in kws] if kws else None

        publicaciones_dicts = filtrar_publicaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tono=tono,
            keywords_relacionadas=keywords,
            busqueda_palabras=busq,
            area_id=area_id,
            fuente_id=fuente_id,
            pais=pais
        )

        if concepto_oid:
            publicaciones_dicts = [
                pub for pub in publicaciones_dicts
                if concepto_oid in pub.get("conceptos_relacionados_ids", [])
            ]

        filtros = {
            "concepto_interes": ci,
            "area_id": ai,
            "fuente_id": fiu,
            "tono": tone,
            "busqueda_palabras": busq,
            "pais": pais,
            "keywordsRelacionadas": kws
        }

        word_file = generar_informe_impacto_temporal(publicaciones_dicts, filtros)
        filename = f"informe_impacto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        return send_file(word_file, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    except ValueError as ve:
        return {"error": f"Parámetro inválido: {ve}"}, 400
    except Exception as e:
        logging.exception("❌ Error inesperado al generar el informe de impacto temporal")
        return {"error": f"Error inesperado: {e}"}, 500




@api_publicaciones.route('/publicaciones_dia', methods=['GET'])
@SerializeJson
def publicaciones_por_dia_endpoint():
    try:
        fi = request.args.get("fechaInicio")
        ff = request.args.get("fechaFin")
        ci = request.args.get("concepto_interes")
        ai = request.args.get("area_id")
        fiu = request.args.get("fuente_id")
        tone = request.args.get("tono")
        kws = request.args.getlist("keywordsRelacionadas")
        busq = request.args.get("busqueda_palabras")
        pais = request.args.get("pais")

        if not fi or not ff:
            return {"error": "Los parámetros fechaInicio y fechaFin son obligatorios"}, 400

        fecha_inicio = datetime.fromisoformat(fi)
        fecha_fin = datetime.fromisoformat(ff)

        concepto_oid = ObjectId(ci) if ci else None
        area_id = ObjectId(ai) if ai else None
        fuente_id = ObjectId(fiu) if fiu else None
        tono = int(tone) if tone else None
        keywords = [ObjectId(k) for k in kws] if kws else None

        publicaciones = filtrar_publicaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tono=tono,
            keywords_relacionadas=keywords,
            busqueda_palabras=busq,
            area_id=area_id,
            fuente_id=fuente_id,
            pais=pais  
        )

        if concepto_oid:
            publicaciones = [
                pub for pub in publicaciones
                if concepto_oid in pub.get("conceptos_relacionados_ids", [])
            ]

        conteo_por_dia = defaultdict(int)
        for pub in publicaciones:
            fecha_pub = pub.get("fecha")
            if fecha_pub:
                fecha_str = fecha_pub.date().isoformat()
                conteo_por_dia[fecha_str] += 1

        datos_publicaciones_dia = [{"datoX": fecha, "datoY": count} for fecha, count in sorted(conteo_por_dia.items())]

        return datos_publicaciones_dia, 200

    except ValueError as ve:
        return {"error": f"Parámetro inválido: {ve}"}, 400
    except Exception as e:
        return {"error": f"Error inesperado: {e}"}, 500


@api_publicaciones.route('/publicaciones_pais', methods=['GET'])
@SerializeJson
def publicaciones_por_pais_endpoint():
    try:
        fi = request.args.get("fechaInicio")
        ff = request.args.get("fechaFin")
        ci = request.args.get("concepto_interes")
        ai = request.args.get("area_id")
        fiu = request.args.get("fuente_id")
        tone = request.args.get("tono")
        kws = request.args.getlist("keywordsRelacionadas")
        busq = request.args.get("busqueda_palabras")
        pais = request.args.get("pais")

        if not fi or not ff:
            return {"error": "Los parámetros fechaInicio y fechaFin son obligatorios"}, 400

        fecha_inicio = datetime.fromisoformat(fi)
        fecha_fin = datetime.fromisoformat(ff)

        concepto_oid = ObjectId(ci) if ci else None
        area_id = ObjectId(ai) if ai else None
        fuente_id = ObjectId(fiu) if fiu else None
        tono = int(tone) if tone else None
        keywords = [ObjectId(k) for k in kws] if kws else None

        publicaciones = filtrar_publicaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tono=tono,
            keywords_relacionadas=keywords,
            busqueda_palabras=busq,
            area_id=area_id,
            fuente_id=fuente_id,
            pais=pais
        )

        if concepto_oid:
            publicaciones = [
                pub for pub in publicaciones
                if concepto_oid in pub.get("conceptos_relacionados_ids", [])
            ]

        conteo_por_pais = defaultdict(int)
        for pub in publicaciones:
            pais_pub = pub.get("pais") or "Desconocido"
            conteo_por_pais[pais_pub] += 1

        datos_publicaciones_pais = [
            {"datoX": str(pais), "datoY": count}
            for pais, count in conteo_por_pais.items()
        ]
        datos_publicaciones_pais.sort(key=lambda x: x["datoX"])

        return datos_publicaciones_pais, 200


    except ValueError as ve:
        return {"error": f"Parámetro inválido: {ve}"}, 400
    except Exception as e:
        return {"error": f"Error inesperado: {e}"}, 500


@api_publicaciones.route('/tono_medio_dia', methods=['GET'])
@SerializeJson
def tono_medio_por_dia_endpoint():
    try:
        fi = request.args.get("fechaInicio")
        ff = request.args.get("fechaFin")
        ci = request.args.get("concepto_interes")
        ai = request.args.get("area_id")
        fiu = request.args.get("fuente_id")
        tone = request.args.get("tono")
        kws = request.args.getlist("keywordsRelacionadas")
        busq = request.args.get("busqueda_palabras")
        pais = request.args.get("pais")

        if not fi or not ff:
            return {"error": "Los parámetros fechaInicio y fechaFin son obligatorios"}, 400

        fecha_inicio = datetime.fromisoformat(fi)
        fecha_fin = datetime.fromisoformat(ff)

        concepto_oid = ObjectId(ci) if ci else None
        area_id = ObjectId(ai) if ai else None
        fuente_id = ObjectId(fiu) if fiu else None
        tono_filtro = int(tone) if tone else None
        keywords = [ObjectId(k) for k in kws] if kws else None

        publicaciones = filtrar_publicaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tono=tono_filtro,
            keywords_relacionadas=keywords,
            busqueda_palabras=busq,
            area_id=area_id,
            fuente_id=fuente_id,
            pais=pais
        )

        if concepto_oid:
            publicaciones = [
                pub for pub in publicaciones
                if concepto_oid in pub.get("conceptos_relacionados_ids", [])
            ]

        tonos_por_dia = defaultdict(list)
        for pub in publicaciones:
            fecha_pub = pub.get("fecha")
            tono = pub.get("tono")
            if fecha_pub is not None and isinstance(tono, int):
                fecha_str = fecha_pub.date().isoformat()
                tonos_por_dia[fecha_str].append(tono)

        datos_tono_medio_dia = [
            {"datoX": fecha, "datoY": sum(tonos) / len(tonos)}
            for fecha, tonos in sorted(tonos_por_dia.items())
        ]

        return datos_tono_medio_dia, 200

    except ValueError as ve:
        return {"error": f"Parámetro inválido: {ve}"}, 400
    except Exception as e:
        return {"error": f"Error inesperado: {e}"}, 500



@api_publicaciones.route('/tono_medio_pais', methods=['GET'])
@SerializeJson
def tono_medio_por_pais_endpoint():
    try:
        fi = request.args.get("fechaInicio")
        ff = request.args.get("fechaFin")
        ci = request.args.get("concepto_interes")
        ai = request.args.get("area_id")
        fiu = request.args.get("fuente_id")
        tone = request.args.get("tono")
        kws = request.args.getlist("keywordsRelacionadas")
        busq = request.args.get("busqueda_palabras")
        pais = request.args.get("pais")

        if not fi or not ff:
            return {"error": "Los parámetros fechaInicio y fechaFin son obligatorios"}, 400

        fecha_inicio = datetime.fromisoformat(fi)
        fecha_fin = datetime.fromisoformat(ff)

        concepto_oid = ObjectId(ci) if ci else None
        area_id = ObjectId(ai) if ai else None
        fuente_id = ObjectId(fiu) if fiu else None
        tono_filtro = int(tone) if tone else None
        keywords = [ObjectId(k) for k in kws] if kws else None

        publicaciones = filtrar_publicaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tono=tono_filtro,
            keywords_relacionadas=keywords,
            busqueda_palabras=busq,
            area_id=area_id,
            fuente_id=fuente_id,
            pais=pais
        )

        if concepto_oid:
            publicaciones = [
                pub for pub in publicaciones
                if concepto_oid in pub.get("conceptos_relacionados_ids", [])
            ]

        tonos_por_pais = defaultdict(list)
        for pub in publicaciones:
            pais_pub = pub.get("pais", "Desconocido")
            tono = pub.get("tono")
            if isinstance(tono, int):
                tonos_por_pais[pais_pub].append(tono)

        datos_tono_medio_pais = [
            {"datoX": pais, "datoY": sum(tonos) / len(tonos)}
            for pais, tonos in sorted(tonos_por_pais.items())
        ]

        return datos_tono_medio_pais, 200

    except ValueError as ve:
        return {"error": f"Parámetro inválido: {ve}"}, 400
    except Exception as e:
        return {"error": f"Error inesperado: {e}"}, 500
