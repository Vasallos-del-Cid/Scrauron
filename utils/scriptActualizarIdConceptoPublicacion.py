from pymongo import MongoClient
from bson import ObjectId

# Conexión a tu base local
# client = MongoClient("mongodb://localhost:27017")
#client = MongoClient("")

db = client["baseDatosScrauron"]

publicaciones = db.publicaciones
conceptos = db.conceptos_interes

# Paso 1: construir mapa inverso { publicacion_id: [concepto_id, ...] }
pub_to_concept_ids = {}

for concepto in conceptos.find({}, {"_id": 1, "publicaciones_relacionadas_ids": 1}):
    concepto_id = concepto["_id"]
    for pub_id in concepto.get("publicaciones_relacionadas_ids", []):
        pub_to_concept_ids.setdefault(pub_id, []).append(concepto_id)

# Paso 2: actualizar cada publicación con el array de conceptos relacionados
for pub_id, conceptos_ids in pub_to_concept_ids.items():
    publicaciones.update_one(
        {"_id": pub_id},
        {"$set": {"conceptos_relacionados_ids": conceptos_ids}}
    )

print("✅ Campo 'conceptos_relacionados_ids' actualizado en publicaciones.")
