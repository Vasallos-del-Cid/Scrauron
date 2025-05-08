# llm_utils.py

import os
from dotenv import load_dotenv
from openai import OpenAI
import ast

# Cargar la API Key desde el entorno
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_descripcion_concepto(nombre_concepto: str) -> str:
    """
    Genera una descripción de 4 frases sobre el concepto dado.
    """
    prompt = (
        f"Redacta un párrafo de 4 frases explicando de manera clara y específica el tema: '{nombre_concepto}'. "
        "Usa lenguaje técnico pero comprensible. No repitas palabras innecesarias."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un redactor experto en comunicación clara y precisa."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un analista experto en inteligencia semántica y taxonomías."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    return ast.literal_eval(response.choices[0].message.content.strip())

def estimar_tono_publicacion(publicacion) -> int:
    """
    Usa el título de una publicación para estimar su tono del 1 (muy negativo) al 10 (muy positivo).
    """
    prompt = (
        f"A partir del siguiente título:\n\n\"{publicacion.titulo}\"\n\n"
        "Valora el tono emocional del contenido implícito en el título, del 1 al 10, "
        "donde 1 es muy negativo, 5 es neutro, y 10 es muy positivo. "
        "Devuelve solo el número entero, sin explicación adicional."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un analista experto en comunicación y análisis emocional de lenguaje."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    tono_str = response.choices[0].message.content.strip()
    try:
        return int(tono_str)
    except ValueError:
        raise ValueError(f"Respuesta inesperada del modelo: {tono_str}")
