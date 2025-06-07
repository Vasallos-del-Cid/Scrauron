from functools import wraps
from flask import jsonify, Response

from app.models.modelUtils.serializerUtils import serialize_mongo


def SerializeJson(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Caso: ya es una respuesta tipo Flask
        if isinstance(result, Response):
            return result

        # Caso: es una tupla con response ya serializado
        if isinstance(result, tuple) and isinstance(result[0], Response):
            return result

        # Caso: es una tupla con un objeto aún no serializado
        if isinstance(result, tuple):
            body, *rest = result
            return jsonify(serialize_mongo(body)), *rest

        # Caso: objeto puro, no serializado
        return jsonify(serialize_mongo(result))
    return wrapper