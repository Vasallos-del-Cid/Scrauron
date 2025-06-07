from flask import Blueprint, request, jsonify

from app.models.modelUtils.SerializeJson import SerializeJson
from app.service.jobs.scraping_job import ejecutar_scraping, iniciar_scheduler_en_segundo_plano, detener_scheduler
from app.models.fuente import Fuente
from app.mongo.mongo_fuentes import get_fuente_by_id  

api_scraping = Blueprint('api_scraping', __name__)

#Endpoints Scraping

@api_scraping.route('/scraping', methods=['GET'])
@SerializeJson
def scraping():
    try:
        fuente_id = request.args.get("fuente_id")
        if not fuente_id:
            return {"error": "Falta el parámetro 'fuente_id' en la URL."}, 400

        fuente = get_fuente_by_id(fuente_id)
        if not fuente:
            return {"error": f"No se encontró ninguna fuente con ID {fuente_id}"}, 404

        resultados = ejecutar_scraping(fuente)

        return {
            "success": True,
            "mensaje": f"Scraping ejecutado para la fuente: {fuente.nombre}",
            "resultados": resultados
        }, 200
    except Exception as e:
        return {"error": f"Error al ejecutar scraping: {str(e)}"}, 500


@api_scraping.route("/scheduler/iniciar", methods=["POST"])
def iniciar_scheduler():
    try:
        iniciar_scheduler_en_segundo_plano()
        return {"message": "Scheduler iniciado"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

@api_scraping.route("/scheduler/detener", methods=["POST"])
def detener_scheduler_endpoint():
    try:
        detener_scheduler()
        return {"message": "Scheduler detenido"}, 200
    except Exception as e:
        return {"error": str(e)}, 500