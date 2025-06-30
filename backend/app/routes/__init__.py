from .routes_fuentes import api_fuentes
from .routes_scraping import api_scraping
from .routes_keywords import api_keywords
from .routes_area_impacto import api_areas_impacto


def register_routes(app):
    app.register_blueprint(api_fuentes)
    app.register_blueprint(api_scraping)
    app.register_blueprint(api_keywords)
    app.register_blueprint(api_areas_impacto)