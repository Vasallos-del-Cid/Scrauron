import os
import time
import json
import subprocess
import re

def obtener_nombre_archivo(url):
    match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9\-]+)\.(com|es)', url)
    return f"resultados_{match.group(1) if match else 'sitio'}.json"

def ejecutar_scraping(url):
    nombre_archivo = obtener_nombre_archivo(url)
    script_dir = os.path.dirname(__file__)
    carpeta_json = os.path.abspath(os.path.join(script_dir, "..", "json"))
    os.makedirs(carpeta_json, exist_ok=True)
    ruta_salida = os.path.join(carpeta_json, nombre_archivo)

    if os.path.exists(ruta_salida):
        os.remove(ruta_salida)

    subprocess.run(["python", "spiders/spider_executor.py", url], check=True)

    timeout = 5
    elapsed = 0
    while not os.path.exists(ruta_salida) and elapsed < timeout:
        time.sleep(0.5)
        elapsed += 0.5

    if not os.path.exists(ruta_salida):
        raise FileNotFoundError(f"No se encontró el archivo de salida: {ruta_salida}")

    with open(ruta_salida, "r", encoding="utf-8") as f:
        return json.load(f)
