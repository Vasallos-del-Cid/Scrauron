from flask import Blueprint, request, jsonify
from .scraper import ejecutar_scraping

api = Blueprint('api', __name__)

@api.route('/scraping', methods=['GET'])
def scraping():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    try:
        resultados = ejecutar_scraping(url)
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
