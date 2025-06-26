from functools import wraps
from flask import Response
import json
from datetime import datetime
from bson import ObjectId
from app.models.modelUtils.serializerUtils import serialize_mongo

def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def SerializeJson(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, Response):
            return result

        if isinstance(result, tuple):
            body, *rest = result
            json_body = json.dumps(serialize_mongo(body), ensure_ascii=False, default=custom_serializer)
            return Response(json_body, mimetype='application/json'), *rest

        json_body = json.dumps(serialize_mongo(result), ensure_ascii=False, default=custom_serializer)
        return Response(json_body, mimetype='application/json')

    return wrapper
