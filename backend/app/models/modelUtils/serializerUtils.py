from functools import wraps
from flask import jsonify

from app.models.modelUtils.SerializeJson import serialize_mongo


def SerializeJson(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Si ya es una respuesta Flask completa, no tocar
        if isinstance(result, tuple):
            body, *rest = result
            return jsonify(serialize_mongo(body)), *rest
        return jsonify(serialize_mongo(result))
    return wrapper
