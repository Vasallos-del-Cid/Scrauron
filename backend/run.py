from flask import Flask
from app.routes.routes_fuentes import api_fuentes
from app.routes.routes_scraping import api_scraping
from app.routes.routes_areas import api_areas
from app.routes.routes_publicaciones import api_publicaciones
from app.routes.routes_conceptos import api_conceptos

app = Flask(__name__)

# Todas las rutas dentro del blueprint tendrán prefijo /api
app.register_blueprint(api_fuentes, url_prefix='/api')
app.register_blueprint(api_scraping, url_prefix='/api')
app.register_blueprint(api_areas, url_prefix='/api')
app.register_blueprint(api_publicaciones, url_prefix='/api')
app.register_blueprint(api_conceptos, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
