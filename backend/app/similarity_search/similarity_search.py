from bson import ObjectId
from datetime import datetime
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models.publicacion import Publicacion
from app.mongo.mongo_conceptos import update_concepto_dict, get_conceptos_dict

# Modelo de embeddings semánticos mejorado
model = SentenceTransformer("intfloat/multilingual-e5-base")

def normalizar_texto(texto):
    return texto.replace("\n", " ").strip()

def construir_indice_conceptos(conceptos):
    textos = [
        normalizar_texto(
            f"{c['nombre']}. {c.get('descripcion', '')}. Temas: {'; '.join(c.get('keywords', []))}"
        )
        for c in conceptos
    ]

    if not textos:
        return None, [], []

    queries = ["query: " + t for t in textos]
    embeddings = model.encode(queries, normalize_embeddings=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    return index, textos, embeddings

def buscar_y_enlazar_a_conceptos(publicacion: Publicacion, top_k=10, umbral_similitud=0.83):
    if not publicacion or not publicacion._id:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Publicación inválida o sin _id.")
        return []

    texto = normalizar_texto(f"{publicacion.titulo}. {publicacion.contenido}")
    emb_pub = model.encode(["query: " + texto], normalize_embeddings=True)[0].astype("float32")

    conceptos = get_conceptos_dict()
    if not conceptos:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ No hay conceptos registrados.")
        return []

    index, textos_concepto, _ = construir_indice_conceptos(conceptos)
    if index is None:
        return []

    D, I = index.search(np.array([emb_pub]), top_k)

    conceptos_actualizados = []
    pub_oid = ObjectId(publicacion._id)

    for i, score in zip(I[0], D[0]):
        if i == -1:
            continue

        similitud = score
        concepto = conceptos[i]

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔎 Evaluando '{concepto['nombre']}' (similitud: {similitud:.4f})")

        if similitud >= umbral_similitud:
            relacionados = concepto.get("publicaciones_relacionadas_ids", [])

            if pub_oid in relacionados:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛑 Ya relacionada con '{concepto['nombre']}'")
                continue

            relacionados.append(pub_oid)
            concepto["publicaciones_relacionadas_ids"] = relacionados

            try:
                update_concepto_dict(concepto)
                conceptos_actualizados.append((concepto["nombre"], similitud))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Relacionada con '{concepto['nombre']}' (similitud: {similitud:.2f})")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error al actualizar concepto: {e}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📉 Similitud insuficiente con '{concepto['nombre']}': {similitud:.2f}")

    return conceptos_actualizados