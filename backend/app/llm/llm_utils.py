# llm_utils.py

# Este módulo utiliza la API de OpenAI para generar descripciones, keywords
# y estimaciones de tono emocional a partir de conceptos o publicaciones.

import os
from dotenv import load_dotenv         # Carga variables de entorno desde un archivo .env
from openai import OpenAI              # Cliente oficial para la API de OpenAI
import ast                             # Permite evaluar strings como estructuras de Python de forma segura
import re
from app.models.publicacion import Publicacion

# Cargar la API Key desde el archivo .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------------------------------------------
# Genera una descripción clara y concisa de un concepto dado
def generar_descripcion_concepto(nombre_concepto: str) -> str:
    """
    Genera una descripción de 4 frases sobre el concepto dado.
    """
    prompt = (
        f"Redacta un párrafo de 4 frases explicando de manera clara y específica el tema: '{nombre_concepto}'. "
        "Usa lenguaje técnico pero comprensible. No repitas palabras innecesarias."
    )

    # Se hace una llamada al modelo GPT-4 con el prompt diseñado
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un redactor experto en comunicación clara y precisa."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7  # Un poco de variabilidad para enriquecer el lenguaje
    )

    # Se devuelve el contenido limpio del mensaje generado
    return response.choices[0].message.content.strip()

# ------------------------------------------------------------------------------
# Extrae 10 keywords representativas a partir de una descripción
def generar_keywords_descriptivos(descripcion_concepto: str) -> list:
    """
    Genera 10 keywords representativas a partir de la descripción del concepto.
    Las keywords pueden tener entre 1 y 4 palabras cada una.
    """
    prompt = (
        f"A partir de esta descripción:\n\n\"{descripcion_concepto}\"\n\n"
        "Devuelve un array de 10 keywords representativas del tema. "
        "Cada keyword puede tener hasta 4 palabras. Deben ser útiles para análisis semántico con IA. "
        "Devuelve solo una lista de Python válida, sin explicación adicional."
    )

    # Solicita al modelo que devuelva una lista sintácticamente válida
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un analista experto en inteligencia semántica y taxonomías."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5  # Menos aleatoriedad, más consistencia en la salida
    )

    # Convierte la respuesta (string) a lista real de Python de forma segura
    return ast.literal_eval(response.choices[0].message.content.strip())

# ------------------------------------------------------------------------------
# Estima el tono emocional del título de una publicación entre 1 (muy negativo) y 10 (muy positivo)
def estimar_tono_publicacion(publicacion) -> int:
    """
    Usa el título de una publicación para estimar su tono del 1 (muy negativo) al 10 (muy positivo).
    Si hay enlaces en el título, los elimina antes del análisis.
    """

    # Elimina enlaces (http, https o www) del título
    titulo_limpio = re.sub(r'https?://\S+|www\.\S+', '', publicacion.titulo).strip()

    prompt = (
        f"A partir del siguiente título:\n\n\"{titulo_limpio}\"\n\n"
        "Valora el tono emocional del contenido implícito en el título, del 1 al 10, "
        "donde 1 es muy negativo, 5 es neutro, y 10 es muy positivo. "
        "Devuelve solo el número entero, sin explicación adicional."
    )

    # Se envía el prompt al modelo para que devuelva un número emocional
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un analista experto en comunicación y análisis emocional de lenguaje."},
            {"role": "user", "content": prompt}
        ],
        temperature=0  # Resultado determinista
    )

    tono_str = response.choices[0].message.content.strip()
    try:
        return int(tono_str)  # Convertimos el resultado a entero
    except ValueError:
        raise ValueError(f"Respuesta inesperada del modelo: {tono_str}")  # Manejo de errores si no devuelve un número

# Resume el contenido de una publicación, reformulando con sinónimos para evitar infracción de copyright
def resumir_contenido_reformulado(publicacion: Publicacion, modelo="gpt-4", max_tokens=600) -> Publicacion:
    """
    Resume y reformula el contenido de una publicación utilizando un LLM.
    El resumen no debe reproducir frases literales del original y debe limitarse a 5 líneas.
    Modifica el objeto Publicacion en memoria y lo devuelve.
    Si el contenido excede los 25,000 caracteres, se recorta automáticamente.
    """
    if not publicacion.contenido.strip():
        raise ValueError("El contenido está vacío o no disponible.")

    # Limitar el contenido a los primeros 25,000 caracteres
    if len(publicacion.contenido) > 25000:
        publicacion.contenido = publicacion.contenido[:25000]

    prompt = (
        "Resume el siguiente artículo en un máximo de 5 líneas. "
        "No copies frases exactas del original: reformula y utiliza sinónimos para evitar infracción de copyright. "
        "El tono debe ser claro, profesional y accesible. Aquí está el artículo:\n\n"
        f"{publicacion.contenido}"
    )

    response = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": "Eres un asistente experto en resumir y reformular artículos de prensa evitando plagio."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7
    )

    resumen = response.choices[0].message.content.strip()
    publicacion.contenido = resumen
    return publicacion
