from bson import ObjectId

def serialize_mongo(obj):
    if isinstance(obj, dict):
        return {k: serialize_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_mongo(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

def deserialize_mongo(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == "_id" and isinstance(v, str):
                try:
                    new_obj[k] = ObjectId(v)
                except Exception:
                    new_obj[k] = v
            else:
                new_obj[k] = deserialize_mongo(v)
        return new_obj
    elif isinstance(obj, list):
        return [deserialize_mongo(item) for item in obj]
    return obj
