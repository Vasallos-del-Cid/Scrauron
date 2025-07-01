import logging
from bson import ObjectId
from datetime import datetime
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models.publicacion import Publicacion
from app.mongo.mongo_conceptos import update_concepto_dict, get_conceptos_dict
from app.mongo.mongo_keywords import get_keywords 
from app.service.llm.llm_utils import evaluar_relacion_llm 

# Modelo de embeddings semánticos
model = SentenceTransformer("intfloat/multilingual-e5-base")

def normalizar_texto(texto):
    return texto.replace("\n", " ").strip()

def construir_indice_conceptos(conceptos):
    textos = []

    for c in conceptos:
        nombre = c.get("nombre", "")
        descripcion = c.get("descripcion", "")
        keyword_objs = c.get("keywords", [])
        nombres_keywords = [kw.get("nombre", "") for kw in keyword_objs if isinstance(kw, dict)]
        texto = f"{nombre}. {descripcion}. {'; '.join(nombres_keywords)}"
        textos.append(normalizar_texto(texto))

    if not textos:
        return None, [], []

    queries = ["query: " + t for t in textos]
    embeddings = model.encode(queries, normalize_embeddings=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    return index, textos, embeddings

def construir_indice_keywords(keywords):
    textos = [normalizar_texto(kw["nombre"]) for kw in keywords if kw.get("nombre")]
    if not textos:
        return None, [], []

    queries = ["query: " + t for t in textos]
    embeddings = model.encode(queries, normalize_embeddings=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    return index, textos, embeddings

def buscar_y_enlazar_a_conceptos(publicacion: Publicacion, top_k=30, umbral_similitud=0.834):
    if not publicacion or not publicacion._id:
        logging.warning(f"⚠️ Publicación inválida o sin _id.")
        return []

    texto = normalizar_texto(f"{publicacion.titulo}. {publicacion.contenido}")
    emb_pub = model.encode(["query: " + texto], normalize_embeddings=True)[0].astype("float32")

    conceptos = get_conceptos_dict()
    if not conceptos:
        logging.info(f"❌ No hay conceptos registrados.")
        return []

    index, textos_concepto, _ = construir_indice_conceptos(conceptos)
    if index is None:
        return []

    D, I = index.search(np.array([emb_pub]), top_k)

    conceptos_enlazados_ids = []

    for i, score in zip(I[0], D[0]):
        if i == -1:
            continue

        similitud = score
        concepto = conceptos[i]
        logging.info(f"🔎 Evaluando '{concepto['nombre']}' (similitud: {similitud:.4f})")

        if similitud >= umbral_similitud* 1.02:
            conceptos_enlazados_ids.append(ObjectId(concepto["_id"]))
            logging.info(f" ✅ Relacionada con '{concepto['nombre']}' (similitud: {similitud:.2f})")
        elif umbral_similitud * 0.98 <= similitud <= umbral_similitud * 1.02:
            # Umbral dentro del ±2%
            logging.info(f"🤖 Consultando LLM para decisión con '{concepto['nombre']}' (similitud: {similitud:.2f})...")
            if evaluar_relacion_llm(publicacion, concepto):
                conceptos_enlazados_ids.append(ObjectId(concepto["_id"]))
                logging.info(f" ✅ Relacionada por LLM con '{concepto['nombre']}'")
            else:
                logging.info(f"❌ LLM no considera relacionada la publicación con '{concepto['nombre']}'")
        else:
            logging.info(f"📉 Similitud insuficiente con '{concepto['nombre']}': {similitud:.2f}")

    return conceptos_enlazados_ids



def obtener_keywords_relacionadas(publicacion, umbral_keyword=0.83, top_k=10):
    texto = normalizar_texto(f"{publicacion.titulo}. {publicacion.contenido}")
    emb_pub = model.encode(["query: " + texto], normalize_embeddings=True)[0].astype("float32")

    keywords = get_keywords()
    if not keywords:
        logging.info("❌ No hay keywords registradas.")
        return []

    index, textos_keywords, _ = construir_indice_keywords(keywords)
    if index is None:
        logging.warning("⚠️ No se pudo construir el índice FAISS de keywords.")
        return []

    D, I = index.search(np.array([emb_pub]), top_k)

    keywords_relacionadas = []
    for i, score in zip(I[0], D[0]):
        if i == -1:
            continue
        if score >= umbral_keyword:
            kw = keywords[i]
            keywords_relacionadas.append({
                "keyword_id": kw["_id"],
                "nombre": kw["nombre"],
                "similitud": round(score, 4)
            })

    return keywords_relacionadas

