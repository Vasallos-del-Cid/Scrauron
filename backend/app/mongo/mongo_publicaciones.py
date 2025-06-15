# mongo_publicaciones.py
import logging

# Este módulo gestiona la persistencia de objetos tipo "Publicacion" en MongoDB.
# Incluye operaciones CRUD y además estima automáticamente el tono emocional de
# la publicación utilizando un modelo LLM antes de guardarla.

from bson import ObjectId

from .mongo_conceptos import get_conceptos
from .mongo_fuentes import get_fuentes
from .mongo_keywords import get_keywords
from .mongo_utils import get_collection
from app.service.llm.llm_utils import estimar_tono_publicacion
from pymongo import DESCENDING  # Importa la constante para ordenar de forma descendente (más reciente primero)
import re

# --------------------------------------------------
# Devuelve el objeto de colección Mongo para acceso directo (útil para spiders, por ejemplo)
def get_publicaciones():
    publicaciones = list(get_collection("publicaciones").find())
    for p in publicaciones:
        p["_id"] = str(p["_id"])  # Convierte ObjectId a string para serializar
    return publicaciones

# --------------------------------------------------
# Recupera una única publicación por su ID
def get_publicacion_by_id(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    pub = get_collection("publicaciones").find_one({"_id": ObjectId(pub_id)})
    if pub:
        pub["_id"] = str(pub["_id"])
    return pub

# --------------------------------------------------
# Crea una nueva publicación en la base de datos
# También estima automáticamente el tono del contenido
def create_publicacion(publicacion):
    # Normalizar campos clave
    url = publicacion.url.strip().lower()
    titulo = publicacion.titulo.strip()

    # Comprobar si ya existe la publicación con mismo título y url
    existe = get_collection("publicaciones").find_one({
        "titulo": titulo,
        "url": url
    })

    if existe:
        logging.info(f"⚠️ Ya existe publicación con URL  : {url}")
        return None

    # Estima el tono usando LLM (basado en el título)
    # try:
    #     tono = estimar_tono_publicacion(publicacion)
    #     publicacion.tono = tono
    #     logging.info(f"🎯 Tono estimado: {tono}")
    # except Exception as e:
    #     logging.error(f"⚠️ Error al estimar el tono: {e}")
    #     publicacion.tono = None

    data = {
        "_id": ObjectId(publicacion._id),
        "titulo": publicacion.titulo,
        "url": publicacion.url,
        "fecha": publicacion.fecha,
        "fuente_id": ObjectId(publicacion.fuente_id),
    }
    data["url"] = url  # Asegura consistencia de formato de URL

    # Limpia el _id si viene vacío
    if "_id" in data and data["_id"] is None:
        del data["_id"]

    insert_result = get_collection("publicaciones").insert_one(data)
    return insert_result

# --------------------------------------------------
# Elimina una publicación por ID
def delete_publicacion(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    result = get_collection("publicaciones").delete_one({"_id": ObjectId(pub_id)})
    return result.deleted_count

# --------------------------------------------------
# Elimina todas las publicaciones de la colección
def delete_all_publicaciones():
    try:
        result = get_collection("publicaciones").delete_many({})
        logging.info(f" 🔴 Se eliminaron {result.deleted_count} publicaciones")
        return result.deleted_count
    except Exception as e:
        logging.error(f"❌ Error eliminando publicaciones:\n{e}")
        # raise e

# --------------------------------------------------
# Actualiza parcialmente una publicación por ID
def update_publicacion(pub_id, data):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")

    # Evita modificar el _id directamente
    if "_id" in data:
        del data["_id"]

    result = get_collection("publicaciones").update_one({"_id": ObjectId(pub_id)}, {"$set": data})
    if result.matched_count == 0:
        return None

    # Devuelve la publicación actualizada
    updated = get_collection("publicaciones").find_one({"_id": ObjectId(pub_id)})
    updated["_id"] = str(updated["_id"])
    return updated


def get_publicaciones_con_conceptos():
    publicaciones_raw = get_publicaciones()
    conceptos_raw = get_conceptos()
    fuentes_raw = get_fuentes()
    keywords_raw = get_keywords()

    # 1. Mapa de fuentes por _id
    fuentes_por_id = {f["_id"]: f for f in fuentes_raw}

    # 2. Mapa de keywords por _id
    keywords_por_id = {kw["_id"]: kw for kw in keywords_raw}

    # 3. Mapa de conceptos por _id
    conceptos_por_id = {}
    publicacion_to_conceptos_map = {}

    for concepto in conceptos_raw:
        concepto_id = str(concepto["_id"])
        conceptos_por_id[concepto_id] = {
            "_id": concepto_id,
            "nombre": concepto.get("nombre"),
            "descripcion": concepto.get("descripcion"),
            "keywords_ids": [str(kid) for kid in concepto.get("keywords_ids", [])]
        }

        for pub_id in concepto.get("publicaciones_relacionadas_ids", []):
            if pub_id:
                str_pub_id = str(pub_id)
                publicacion_to_conceptos_map.setdefault(str_pub_id, []).append(concepto_id)

    # 4. Procesar publicaciones con conceptos, fuente y keywords
    publicaciones_resultado = []

    for pub in publicaciones_raw:
        pub_id = str(pub["_id"])
        pub["_id"] = pub_id

        # --- Solo incluir si tiene al menos un concepto relacionado
        if pub_id not in publicacion_to_conceptos_map:
            continue

        # --- Reemplazar fuente
        fuente_id = str(pub.get("fuente_id"))
        pub["fuente"] = fuentes_por_id.get(fuente_id, None)

        # --- Reemplazar keywords por objetos completos
        keywords_ids = pub.get("keywords_relacionadas_ids", [])
        pub["keywords"] = [keywords_por_id.get(str(kid)) for kid in keywords_ids if str(kid) in keywords_por_id]
        pub.pop("keywords_relacionadas_ids", None)

        # --- Reemplazar conceptos relacionados
        conceptos_embebidos = []
        for concepto_id in publicacion_to_conceptos_map[pub_id]:
            if concepto_id in conceptos_por_id:
                conceptos_embebidos.append(conceptos_por_id[concepto_id])
        pub["conceptos_relacionados"] = conceptos_embebidos

        publicaciones_resultado.append(pub)

    return publicaciones_resultado



def filtrar_publicaciones(fecha_inicio, fecha_fin, concepto_interes=None, tono=None, keywords_relacionadas=None, busqueda_palabras=None):

    # Lista de condiciones a aplicar en la consulta
    condiciones = [
        {"fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}
    ]

    if tono is not None:
        condiciones.append({"tono": tono})

    if keywords_relacionadas:
        condiciones.append({"keywords_relacionadas_ids": {"$all": keywords_relacionadas}})

    if busqueda_palabras:
        regex = re.compile(busqueda_palabras, re.IGNORECASE)
        condiciones.append({
            "$or": [
                {"titulo": {"$regex": regex}},
                {"contenido": {"$regex": regex}}
            ]
        })

    # Combina las condiciones con AND
    query = {"$and": condiciones} if len(condiciones) > 1 else condiciones[0]

    # Consulta MongoDB
    publicaciones = list(get_collection("publicaciones").find(query).sort("fecha", DESCENDING))

    # Filtro por concepto (post-procesado)
    if concepto_interes:
        concepto = get_collection("conceptos_interes").find_one({"_id": ObjectId(concepto_interes)})
        if not concepto:
            return []
        publicaciones_relacionadas_ids = {str(pid) for pid in concepto.get("publicaciones_relacionadas_ids", [])}
        publicaciones = [
            pub for pub in publicaciones
            if str(pub["_id"]) in publicaciones_relacionadas_ids
        ]

    # Normaliza para serialización
    for pub in publicaciones:
        pub["_id"] = str(pub["_id"])
        pub["fuente_id"] = str(pub["fuente_id"])
        pub["keywords_relacionadas_ids"] = [str(kid) for kid in pub.get("keywords_relacionadas_ids", [])]

    return publicaciones

