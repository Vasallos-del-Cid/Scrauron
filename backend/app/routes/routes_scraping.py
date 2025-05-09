from flask import Blueprint, request, jsonify

from app.jobs.scraping_job import ejecutar_scraping

api_scraping = Blueprint('api_scraping', __name__)

#Endpoints Scraping

@api_scraping.route('/scraping', methods=['GET'])
def scraping():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    try:
        resultados = ejecutar_scraping(url)

        return jsonify({"Success": f"Realizado scraping"}), 200


    except Exception as e:
        return jsonify({"error": str(e)}), 500
