from flask import Blueprint, request, jsonify
from app.service.jobs.scraping_job import ejecutar_scraping, iniciar_scheduler_en_segundo_plano, detener_scheduler
from app.models.fuente import Fuente
from app.mongo.mongo_fuentes import get_fuente_by_id  

api_scraping = Blueprint('api_scraping', __name__)

#Endpoints Scraping

@api_scraping.route('/scraping', methods=['GET'])
def scraping():
    try:
        fuente_id = request.args.get("fuente_id")
        if not fuente_id:
            return jsonify({"error": "Falta el parámetro 'fuente_id' en la URL."}), 400

        fuente = get_fuente_by_id(fuente_id)
        if not fuente:
            return jsonify({"error": f"No se encontró ninguna fuente con ID {fuente_id}"}), 404

        resultados = ejecutar_scraping(fuente)

        return jsonify({
            "success": True,
            "mensaje": f"Scraping ejecutado para la fuente: {fuente.nombre}",
            "resultados": resultados
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al ejecutar scraping: {str(e)}"}), 500


@api_scraping.route("/scheduler/iniciar", methods=["POST"])
def iniciar_scheduler():
    try:
        iniciar_scheduler_en_segundo_plano()
        return jsonify({"message": "Scheduler iniciado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_scraping.route("/scheduler/detener", methods=["POST"])
def detener_scheduler_endpoint():
    try:
        detener_scheduler()
        return jsonify({"message": "Scheduler detenido"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500