from flask import Blueprint, request, jsonify
from ..scraper import ejecutar_scraping
from ..mongo.mongo_fuentes import get_fuentes, create_fuente, delete_fuente, update_fuente
from ..models.fuente import Fuente

api_scraping = Blueprint('api_scraping', __name__)

#Endpoints Scraping

@api_scraping.route('/scraping', methods=['GET'])
def scraping():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    try:
        resultados = ejecutar_scraping(url)
        return jsonify({"Success": f"Realizado scraping, capturados {len(resultados) if resultados else 0}"}), 200


    except Exception as e:
        return jsonify({"error": str(e)}), 500
