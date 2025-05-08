# llm_utils.py
# Este módulo utiliza la API de OpenAI para generar descripciones, keywords
# y estimaciones de tono emocional a partir de conceptos o publicaciones.

import logging
import os
from dotenv import load_dotenv  # Carga variables de entorno desde un archivo .env
from openai import OpenAI, RateLimitError  # Cliente oficial para la API de OpenAI
import ast  # Permite evaluar strings como estructuras de Python de forma segura
import re
from app.models.publicacion import Publicacion

def get_openai_client():
    global open_ai_client
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not api_key.startswith("sk-"):
        raise Exception("❌ Falta la variable OPENAI_API_KEY en el entorno.")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Modelo de OpenAI a utilizar

    # en caso que este configurado por limite el uso de chatgpt, se puede usar open router
    if "true" == os.getenv("USE_OPEN_ROUTER", "false").lower():
        # Si se usa open router, se debe usar el cliente de open router
        logging.info("Usando OpenRouter como cliente de OpenAI.")
        open_ai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPEN_ROUTER_API_KEY"),
        )
        model = f"openai/{model}"  # Cambia el modelo para que sea compatible con open router
    else:
        open_ai_client = OpenAI(api_key=api_key)
    return open_ai_client, model


def get_gpt_response(messages, temperature):
    """
    Envía un mensaje a la API de OpenAI y devuelve la respuesta generada.
    :param messages:
    :param temperature:
    :return:
    """

    # Cargar la API Key desde el archivo .env
    client, model = get_openai_client()
    response = None
    try:
        response = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
        response = response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error al generar la descripción del concepto: \n{e}")
        raise e
    except RateLimitError as e:
        logging.error("🚫 Límite de cuota alcanzado. Verifica tu facturación en OpenAI.\n La IA no puede generar una respuesta en este momento: se ha alcanzado el límite de uso.")
        raise e
    # Se devuelve el contenido limpio del mensaje generado
    return response if response else "Error al obtener respuesta de la IA."

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
    messages = [
        {"role": "system", "content": "Eres un redactor experto en comunicación clara y precisa."},
        {"role": "user", "content": prompt}
    ]

    response = get_gpt_response(messages, 0.7)
    return response if response else "Error al generar la descripción."


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
    messages = [
        {"role": "system", "content": "Eres un analista experto en inteligencia semántica y taxonomías."},
        {"role": "user", "content": prompt}
    ]

    try:
        # Solicita al modelo que devuelva una lista sintácticamente válida
        response = get_gpt_response(messages, 0.5)
        if not response:
            raise ValueError("Respuesta vacía del modelo.")

        # Limpieza si viene con ```python
        def limpiar_respuesta_de_codigo(respuesta: str) -> str:
            if respuesta.startswith("```") and respuesta.endswith("```"):
                lineas = respuesta.strip().splitlines()
                return "\n".join(lineas[1:-1]).strip()
            return respuesta.strip()

        keywords = ast.literal_eval(limpiar_respuesta_de_codigo(response))


        if not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
            raise TypeError("La respuesta no es una lista de strings válida.")

        return keywords

    except (ValueError, SyntaxError, TypeError) as e:
        logging.error(f"❌ Error al generar keywords: {e}\nRespuesta recibida: {response}")
        raise e

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
    messages = [
        {"role": "system", "content": "Eres un analista experto en comunicación y análisis emocional de lenguaje."},
        {"role": "user", "content": prompt}
    ]

    # Se envía el prompt al modelo para que devuelva un número emocional
    tono_str = get_gpt_response(messages, 0)
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
