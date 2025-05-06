import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models.publicacion import Publicacion
from app.mongo.mongo_areas import get_areas, update_area

# Modelo de embeddings semánticos
model = SentenceTransformer("all-MiniLM-L6-v2")

def construir_indice_conceptos(conceptos):
    textos = [c.nombre + " " + " ".join(c.keywords) for c in conceptos]
    if not textos:
        return None, [], []

    # Embeddings normalizados para cosine similarity
    embeddings = model.encode(textos, normalize_embeddings=True)
    dim = embeddings.shape[1]

    # Índice de producto interno (IP) que funciona como cosine similarity
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    return index, textos, embeddings

def buscar_y_enlazar_a_conceptos(publicacion: Publicacion, top_k=1, umbral_similitud=0.2):
    if not publicacion or not publicacion._id:
        print("⚠️ Publicación inválida o sin _id. No se puede enlazar a conceptos.")
        return []

    # Texto base para vector semántico
    texto = f"{publicacion.titulo} {publicacion.contenido}"
    emb_pub = model.encode([texto], normalize_embeddings=True)[0].astype("float32")

    conceptos_actualizados = []

    for area in get_areas():
        conceptos = area.conceptos_interes
        if not conceptos:
            continue

        index, textos_concepto, _ = construir_indice_conceptos(conceptos)
        if index is None:
            continue

        # Búsqueda en el índice
        D, I = index.search(np.array([emb_pub]), top_k)

        actualizado = False

        for i, score in zip(I[0], D[0]):
            if i == -1:
                continue  # FAISS no encontró resultado
            
            similitud = score  # producto interno ya es cosine similarity
            print("SIMILITUD: ",similitud, "UMBRAL:", umbral_similitud)
            if similitud >= umbral_similitud:
                print(f" Encontrada similitud con '{concepto.nombre}'")
                concepto = conceptos[i]

                # Verifica si ya está relacionada
                ya_relacionada = any(pub.url == publicacion.url for pub in concepto.publicaciones_relacionadas)
                if ya_relacionada:
                    print(f"🛑 Publicación ya relacionada con '{concepto.nombre}'")
                    continue

                # Añadir publicación relacionada
                concepto.publicaciones_relacionadas.append(publicacion)
                conceptos_actualizados.append((area.nombre, concepto.nombre, similitud))
                actualizado = True

        # Si hubo cambios, actualizamos el área
        if actualizado:
            try:
                update_area(area)
                print(f"✅ Área actualizada: {area.nombre}")
            except Exception as e:
                print(f"❌ Error actualizando el área '{area.nombre}': {e}")

    for area_nombre, concepto_nombre, sim in conceptos_actualizados:
        print(f"📌 Publicación enlazada con '{concepto_nombre}' del área '{area_nombre}' (similitud: {sim:.2f})")

    return conceptos_actualizados
