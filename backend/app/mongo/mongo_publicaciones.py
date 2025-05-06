import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from ..models.publicacion import Publicacion

# Conexión a MongoDB (igual que en fuentes)
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["baseDatosScrauron"]
coleccion = db["publicaciones"]

#Indice único combinación de título u url. Evita duplicados en BBDD.
coleccion.create_index(
    [("titulo", 1), ("url", 1)],
    unique=True,
    name="titulo_url_unique"
)

#GET COLLECTION
def get_mongo_collection():
    return coleccion
#GET
def get_publicaciones():
    publicaciones = list(coleccion.find())
    for p in publicaciones:
        p["_id"] = str(p["_id"])
    return publicaciones

def get_publicacion_by_id(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    pub = coleccion.find_one({"_id": ObjectId(pub_id)})
    if pub:
        pub["_id"] = str(pub["_id"])
    return pub

#POST
def create_publicacion(publicacion):
    url = publicacion.url.strip().lower()

    existe = coleccion.find_one({"url": url})

    if existe:
        print(f"⚠️ Ya existe publicación con URL: {url}")
        return None

    data = publicacion.to_dict()

    # Normalizar también antes de guardar
    data["url"] = url

    if "_id" in data and data["_id"] is None:
        del data["_id"]

    insert_result = coleccion.insert_one(data)
    print(f"✅ Publicación creada: {url}")
    return insert_result
#DELETE
def delete_publicacion(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    result = coleccion.delete_one({"_id": ObjectId(pub_id)})
    return result.deleted_count

#UPDATE
def update_publicacion(pub_id, data):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    if "_id" in data:
        del data["_id"]
    result = coleccion.update_one({"_id": ObjectId(pub_id)}, {"$set": data})
    if result.matched_count == 0:
        return None
    updated = coleccion.find_one({"_id": ObjectId(pub_id)})
    updated["_id"] = str(updated["_id"])
    return updated
