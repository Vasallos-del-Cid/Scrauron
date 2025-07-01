# Importación de librerías necesarias
from flask import Blueprint, request, jsonify  # Para definir rutas y manejar peticiones HTTP
from datetime import datetime  # Para manejar fechas
import logging  # Para registrar errores
from bson import ObjectId  # Para trabajar con IDs de MongoDB

# Importaciones del proyecto (módulos propios)
from app.mongo.mongo_publicaciones import filtrar_publicaciones  # Función para filtrar noticias
from ..service.llm.llm_utils import procesar_en_lotes_para_informe  # Procesa publicaciones para generar informe
from app.models.publicacion import Publicacion  # Modelo de datos para publicaciones
from ..models.informe_impacto import InformeImpacto  # Modelo del informe de impacto
from ..models.modelUtils.SerializeJson import SerializeJson  # Decorador para serializar respuestas JSON
from ..mongo.mongo_informes_impacto import (
    create_informe,  # Crear un nuevo informe en la BBDD
    get_informe_by_id,  # Obtener informe por ID
    get_informes_by_area_de_trabajo,  # Obtener informes por área
    update_informe,  # Actualizar informe
    delete_informe  # Eliminar informe
)

# Crear un "blueprint" de Flask para agrupar rutas relacionadas
api_informes_impacto = Blueprint('api_informes_impacto', __name__)

# Ruta GET: lista informes por área
@api_informes_impacto.route('/informes_impacto/<area_id>', methods=['GET'])
@SerializeJson  # Serializa automáticamente las respuestas
def listar_informes_por_area(area_id):
    try:
        informes = get_informes_by_area_de_trabajo(area_id)
        return [inf.to_dict() for inf in informes], 200
    except Exception as e:
        return {"error": str(e)}, 500

# Ruta GET: genera un informe a partir de parámetros pasados por query string
@api_informes_impacto.route('/informe_impacto', methods=['GET'])
def generar_informe_endpoint():
    try:
        # Recuperar parámetros de la petición
        fi = request.args.get("fechaInicio")
        ff = request.args.get("fechaFin")
        fiu = request.args.get("fuente_id")
        tone = request.args.get("tono")
        kws = request.args.getlist("keywordsRelacionadas")
        busq = request.args.get("busqueda_palabras")
        pais = request.args.get("pais")

        # Validación básica
        if not fi or not ff:
            return {"error": "Parámetros obligatorios: fechaInicio, fechaFin"}, 400

        # Conversión de parámetros a tipos adecuados
        fecha_inicio = datetime.fromisoformat(fi)
        fecha_fin = datetime.fromisoformat(ff)
        fuente_id = ObjectId(fiu) if fiu else None
        tono = int(tone) if tone else None
        keywords = [ObjectId(k) for k in kws] if kws else None

        # Filtrado de publicaciones según los parámetros
        publicaciones = filtrar_publicaciones(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tono=tono,
            keywords_relacionadas=keywords,
            busqueda_palabras=busq,
            fuente_id=fuente_id,
            pais=pais
        )

        # Convertir diccionarios a objetos Publicacion
        publicaciones_objs = [Publicacion.from_dict(p) for p in publicaciones]

        if not publicaciones_objs:
            return {"error": "No se encontraron publicaciones para los parámetros dados."}, 404

        # Tomar el área de trabajo desde la primera publicación
        area_de_trabajo_id = publicaciones_objs[0].area_id if publicaciones_objs[0].area_id else None

        if not area_de_trabajo_id:
            return {"error": "No se pudo determinar el área de trabajo de las publicaciones."}, 400

        # Generar informe usando función LLM
        informe = procesar_en_lotes_para_informe(publicaciones_objs, area_de_trabajo_id=str(area_de_trabajo_id))
        return jsonify(informe), 200

    except Exception as e:
        logging.error(f"Error generando informe de impacto: {e}")
        return {"error": str(e)}, 500

# Ruta POST: crea un nuevo informe en la base de datos
@api_informes_impacto.route('/informes_impacto', methods=['POST'])
def crear_informe_endpoint():
    data = request.get_json()
    try:
        informe = InformeImpacto.from_dict(data)
        result = create_informe(informe)
        informe._id = str(result.inserted_id)
        return informe.to_dict(), 201
    except Exception as e:
        return {"error": str(e)}, 400

# Ruta PATCH: actualiza un informe existente
@api_informes_impacto.route('/informes_impacto/<informe_id>', methods=['PATCH'])
def actualizar_informe_endpoint(informe_id):
    data = request.get_json()
    try:
        doc = get_informe_by_id(informe_id)
        if not doc:
            return {"error": "Informe no encontrado"}, 404
        informe = InformeImpacto.from_dict(doc)

        # Solo se actualiza el campo impactos si está presente
        if 'impactos' in data:
            informe.impactos = data['impactos']

        update_informe(informe)
        return informe.to_dict(), 200
    except Exception as e:
        return {"error": str(e)}, 500

# Ruta DELETE: elimina un informe por su ID
@api_informes_impacto.route('/informes_impacto/<informe_id>', methods=['DELETE'])
def eliminar_informe_endpoint(informe_id):
    try:
        deleted = delete_informe(informe_id)
        if deleted == 0:
            return {"error": "Informe no encontrado"}, 404
        return '', 204
    except Exception as e:
        return {"error": str(e)}, 500
