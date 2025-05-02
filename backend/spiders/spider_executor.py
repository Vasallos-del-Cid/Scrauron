import sys
import os
from scrapy.crawler import CrawlerProcess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from spiders.spider import NoticiasSpider  
from spiders.spider_telegram import TelegramSpider

def obtener_nombre_archivo(url):
    import re
    match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9\-]+)\.(com|es)', url)
    return f"resultados_{match.group(1) if match else 'sitio'}.json"

if __name__ == "__main__":
    # Obtener la URL pasada como argumento
    url = sys.argv[1]
    nombre_archivo = obtener_nombre_archivo(url)

    # Obtener el directorio actual
    base_dir = os.path.dirname(os.path.abspath(__file__))
    carpeta_json = os.path.abspath(os.path.join(base_dir, "..", "json"))
    os.makedirs(carpeta_json, exist_ok=True)  # Asegurarse de que la carpeta exista

    # Ruta completa del archivo de salida
    ruta_salida = os.path.join(carpeta_json, nombre_archivo)

    # Configuración y ejecución de Scrapy
    process = CrawlerProcess(settings={
        "FEEDS": {
            ruta_salida: {"format": "json", "encoding": "utf8", "indent": 4}
        },
        "LOG_ENABLED": False  # Deshabilitar logs si no los necesitas
    })
    if(url.startswith(("https://t.me/", "http://t.me/"))):
        print("Detectado Telegram")
    process.crawl(TelegramSpider if url.startswith(("https://t.me/", "http://t.me/")) else NoticiasSpider, url=url)

    process.start()
