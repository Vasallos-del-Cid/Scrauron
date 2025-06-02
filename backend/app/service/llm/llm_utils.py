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
from app.models.keyword import Keyword
from app.mongo.mongo_keywords import create_keyword
import json

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
        f"Redacta un párrafo de 4 frases explicando de manera clara y específica el tema: '{nombre_concepto}'. Desde un punto de vista de la actualidad y las noticias publicadas"
        "Usa lenguaje técnico pero comprensible. No repitas palabras innecesarias. No uses comillas ni comillas dobles."
    )
    messages = [
        {"role": "system", "content": "Eres un redactor experto en comunicación clara y precisa."},
        {"role": "user", "content": prompt}
    ]

    response = get_gpt_response(messages, 0.7)
    return response if response else "Error al generar la descripción."


# ------------------------------------------------------------------------------
# Extrae y guarda 10 keywords representativas a partir de una descripción
def generar_keywords_descriptivos(descripcion_concepto: str) -> list[Keyword]:
    """
    Genera 10 keywords a partir de la descripción del concepto,
    las guarda en Mongo (si no existen) y devuelve objetos Keyword con _id.
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
        response = get_gpt_response(messages, 0.5)
        if not response:
            raise ValueError("Respuesta vacía del modelo.")

        def limpiar_respuesta_de_codigo(respuesta: str) -> str:
            if respuesta.startswith("```") and respuesta.endswith("```"):
                lineas = respuesta.strip().splitlines()
                return "\n".join(lineas[1:-1]).strip()
            return respuesta.strip()

        raw_keywords = ast.literal_eval(limpiar_respuesta_de_codigo(response))

        if not isinstance(raw_keywords, list) or not all(isinstance(k, str) for k in raw_keywords):
            raise TypeError("La respuesta no es una lista de strings válida.")

        keywords_guardadas = []

        for nombre in raw_keywords:
            nombre_limpio = nombre.strip()
            keyword_obj = Keyword(nombre=nombre_limpio)

            # Guardar usando create_keyword
            respuesta, status = create_keyword(keyword_obj)

            if status in (200, 201):  # ya existe o se acaba de crear
                json_data = respuesta.get_json()
                keyword_obj._id = json_data.get("_id")
                keywords_guardadas.append(keyword_obj)
            else:
                logging.warning(f"No se pudo guardar la keyword: {nombre_limpio} (status {status})")

        return keywords_guardadas

    except (ValueError, SyntaxError, TypeError) as e:
        logging.error(f"❌ Error al generar o guardar keywords: {e}\nRespuesta recibida: {response}")
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
def resumir_contenido_reformulado(publicacion: Publicacion, keywords_dict=None, max_tokens=600) -> Publicacion:
    """
    Resume y reformula el contenido de una publicación utilizando un LLM.
    Se incorporan las keywords relacionadas (por ID) si están disponibles.
    El resumen evita frases literales y debe mantenerse entre 6 y 10 líneas.
    """
    if not publicacion.contenido.strip():
        raise ValueError("El contenido está vacío o no disponible.")

    if len(publicacion.contenido) > 15000:
        publicacion.contenido = publicacion.contenido[:15000]

    # Extraer nombres de keywords si están disponibles
    keyword_nombres = []
    if hasattr(publicacion, "keywords_relacionadas_ids") and publicacion.keywords_relacionadas_ids:
        if keywords_dict is not None:
            keyword_nombres = [keywords_dict.get(str(kid), "") for kid in publicacion.keywords_relacionadas_ids]
        else:
            # Si no se pasa el diccionario, obtenerlas directamente (esto requiere acceso a Mongo)
            from app.mongo.mongo_keywords import get_keywords_by_ids
            keywords = get_keywords_by_ids(publicacion.keywords_relacionadas_ids)
            keyword_nombres = [kw["nombre"] for kw in keywords if "nombre" in kw]

    prompt = (
        "Resume el siguiente artículo en un mínimo de 6 y un máximo de 10 líneas. "
        "Evita repetir frases textuales del texto original: reformula con sinónimos y un estilo claro. "
        "Enfócate especialmente en los temas relacionados con las siguientes palabras clave:\n\n"
        f"{', '.join(keyword_nombres)}\n\n"
        "El tono debe ser profesional y directo. Aquí está el texto completo del artículo:\n\n"
        f"{publicacion.contenido}"
    )

    messages = [
        {"role": "system", "content": "Eres un asistente experto en resumir y reformular artículos de prensa evitando plagio."},
        {"role": "user", "content": prompt}
    ]

    resumen = get_gpt_response(messages, temperature=0.7)
    publicacion.contenido = resumen
    return publicacion



def analizar_publicacion(publicacion, max_tokens=600):
    """
    Analiza una publicación:
    - Resume y reformula el contenido.
    - Estima el tono emocional del título (1-10).
    
    Devuelve el objeto Publicacion con:
    - contenido: actualizado con el resumen.
    - tono: nuevo atributo con el valor del tono emocional.
    """
    if not publicacion.contenido.strip():
        raise ValueError("El contenido está vacío o no disponible.")

    if len(publicacion.contenido) > 25000:
        publicacion.contenido = publicacion.contenido[:25000]

    titulo_limpio = re.sub(r'https?://\S+|www\.\S+', '', publicacion.titulo).strip()

    prompt = (
        f"Título: \"{titulo_limpio}\"\n\n"
        f"Contenido:\n{publicacion.contenido}\n\n"
        "Primero, resume el artículo en un máximo de 5 líneas, reformulando con sinónimos para evitar copiar frases literales.\n"
        "Después, valora el tono emocional implícito en el título del 1 (muy negativo) al 9 (muy positivo). Y 5 neutro.\n\n"
        "Devuelve el resultado únicamente en formato JSON con las claves: { 'resumen': ..., 'tono': ... } . Dame únicamente las llaves y su contenido, no lo envuelvas con ```json y usa en el json comillas dobles"
    )

    messages = [
        {"role": "system", "content": "Eres un asistente experto en análisis de prensa, resumen profesional y valoración emocional del lenguaje."},
        {"role": "user", "content": prompt}
    ]

    respuesta = get_gpt_response(messages, temperature=0.7)

    try:
        resultado = json.loads(respuesta)
        publicacion.contenido = resultado['resumen']
        publicacion.tono = int(resultado['tono'])  # Agregamos el atributo "tono"
        logging.info(f"🎯 Tono estimado: {publicacion.tono}")
        logging.info(f"✅ Resumen creado: {publicacion.contenido}")
        return publicacion
    except (json.JSONDecodeError, KeyError, ValueError):
        raise ValueError(f"Respuesta inesperada del modelo, se esperaba JSON con claves 'resumen' y 'tono': {respuesta}")
