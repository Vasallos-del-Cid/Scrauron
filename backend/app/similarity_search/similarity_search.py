import logging

from bson import ObjectId
from datetime import datetime
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models.publicacion import Publicacion
from app.mongo.mongo_conceptos import update_concepto_dict, get_conceptos_dict

# Modelo de embeddings semánticos mejorado
model = SentenceTransformer("intfloat/multilingual-e5-base")

# Elimina saltos de línea y espacios sobrantes
def normalizar_texto(texto):
    return texto.replace("\n", " ").strip()

#Construye un índice FAISS a partir de los embeddings semánticos de las keywords de todos los conceptos, optimizados para búsquedas por similitud coseno
def construir_indice_conceptos(conceptos):
    textos = []

    # Construimos textos para cada concepto con las keywords
    for c in conceptos:
        keywords = "; ".join(c.get("keywords", []))
        texto = f"{keywords}"
        textos.append(normalizar_texto(texto))

    # Si no hay textos, no construimos índice
    if not textos:
        return None, [], []

    # Prefijamos con "query:" para optimizar compatibilidad con el modelo e5
    queries = ["query: " + t for t in textos]

    # Generamos embeddings normalizados para usar similitud coseno (con producto escalar)
    embeddings = model.encode(queries, normalize_embeddings=True)

    # Creamos el índice FAISS con producto escalar como métrica
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    return index, textos, embeddings

# Analiza una publicación, calcula su similitud semántica con todos los conceptos registrados y, si supera un umbral, asocia su ID a los conceptos relevantes en la base de datos.

def buscar_y_enlazar_a_conceptos(publicacion: Publicacion, top_k=30, umbral_similitud=0.85):
    # Verifica que la publicación sea válida y tenga un ID asignado
    if not publicacion or not publicacion._id:
        logging.warning(f"⚠️ Publicación inválida o sin _id.")
        return []

    # Prepara el texto combinando título y contenido, y lo normaliza (quita saltos, espacios, etc.)
    texto = normalizar_texto(f"{publicacion.titulo}. {publicacion.contenido}")

    # Genera el embedding semántico del texto con el prefijo 'query:' (usado por modelos tipo e5)
    emb_pub = model.encode(["query: " + texto], normalize_embeddings=True)[0].astype("float32")

    # Recupera todos los conceptos desde MongoDB en formato dict
    conceptos = get_conceptos_dict()
    if not conceptos:
        logging.info(f"❌ No hay conceptos registrados.")
        return []

    # Construye el índice semántico FAISS a partir de los conceptos
    index, textos_concepto, _ = construir_indice_conceptos(conceptos)
    if index is None:
        return []

    # Busca los top_k conceptos más similares a la publicación en el índice
    D, I = index.search(np.array([emb_pub]), top_k)

    # Lista para almacenar los conceptos a los que se asocia la publicación
    conceptos_actualizados = []
    pub_oid = ObjectId(publicacion._id)  # Asegura que el ID esté en formato BSON

    # Itera sobre los resultados (índices y scores)
    for i, score in zip(I[0], D[0]):
        if i == -1:
            continue  # Resultado nulo (no hay suficiente para top_k)

        similitud = score
        concepto = conceptos[i]

        # Muestra en consola información del concepto y su similitud
        logging.info(f" 🔎 Evaluando '{concepto['nombre']}' (similitud: {similitud:.4f})")

        # Verifica si la similitud es suficientemente alta para enlazar
        if similitud >= umbral_similitud:
            relacionados = concepto.get("publicaciones_relacionadas_ids", [])

            # Evita duplicar el ID de la publicación si ya está relacionado
            if pub_oid in relacionados:
                logging.error(f"🛑 Ya relacionada con '{concepto['nombre']}'")
                continue

            # Añade el ID de la publicación a la lista del concepto
            relacionados.append(pub_oid)
            concepto["publicaciones_relacionadas_ids"] = relacionados

            try:
                # Actualiza el concepto en la base de datos
                update_concepto_dict(concepto)
                conceptos_actualizados.append((concepto["nombre"], similitud))
            except Exception as e:
                # Captura errores de actualización
                logging.error(f"❌ Error al actualizar concepto: {e}")
        else:
            # Muestra conceptos cuya similitud es demasiado baja
            logging.info(f"📉 Similitud insuficiente con '{concepto['nombre']}': {similitud:.2f}")

    # Devuelve la lista de conceptos actualizados con los que hubo relación
    return conceptos_actualizados
