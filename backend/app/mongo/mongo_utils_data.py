from app.mongo.mongo_utils import get_db


class MongoJoinService:
    def __init__(self):
        self.db = get_db()

    def join_collections(self, collection_a, collection_b, local_field, foreign_field, as_field=None, match_filter=None):
        as_field = as_field or collection_b
        pipeline = []

        if match_filter:
            pipeline.append({"$match": match_filter})

        pipeline.append({
            "$lookup": {
                "from": collection_b,
                "localField": local_field,
                "foreignField": foreign_field,
                "as": as_field
            }
        })

        return list(self.db[collection_a].aggregate(pipeline))


