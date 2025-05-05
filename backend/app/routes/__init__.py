from .routes_fuentes import api_fuentes
from .routes_scraping import api_scraping

def register_routes(app):
    app.register_blueprint(api_fuentes)
    app.register_blueprint(api_scraping)
