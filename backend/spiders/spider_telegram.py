import scrapy
from scrapy_playwright.page import PageMethod
import os
import argparse
from scrapy.crawler import CrawlerProcess
import re
from db import coleccion

class TelegramSpider(scrapy.Spider):
    name = "telegram"
    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30 * 1000,
    }
    url=""
    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else ["https://t.me/s/Alviseperez"]

    def start_requests(self):
        for url in self.start_urls:
            self.url = url
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", ".tgme_widget_message")
                    ]
                }
            )

    def parse(self, response):
        for msg in response.css(".tgme_widget_message_wrap"):
            # El contenido será el resto del mensaje
            contenido = msg.css(".tgme_widget_message_text").xpath("string()").get()

            # Extraemos el texto hasta el primer ":" o "."
            match = re.match(r"^(.*?)(:|\.)", contenido)
            if match:
                titulo = match.group(1).strip()  # El texto antes del ":" o "."
            else:
                titulo = "Sin título"  # En caso de no encontrar ":" o ".", asignamos un título por defecto

            # Si no hay contenido, se asigna un título por defecto
            if not contenido:
                contenido = "Sin contenido"

            yield {
                "titulo": titulo,
                "url": self.url,
                "contenido": contenido
            }
            noticia={
                "titulo": titulo,
                "url": self.url,
                "contenido": contenido
            }
            resultado = coleccion.insert_one(noticia)

def run_spider(url):
    # Obtener la ruta del directorio actual donde se encuentra el script (noticias_scraper/spiders)
    script_dir = os.path.dirname(__file__)
    
    # Crear una ruta relativa a la carpeta 'json' que se encuentra en el directorio principal 'noticias_scraper'
    output_dir = os.path.join(script_dir, "..", "json")  # Subir un nivel y luego acceder a 'json'
    
    # Asegurarse de que la carpeta 'json' exista
    os.makedirs(output_dir, exist_ok=True)
    
    # Crear el nombre del archivo de salida
    output_file = os.path.join(output_dir, "resultados_telegram.json")
    
    process = CrawlerProcess(settings={
        "FEEDS": {
            output_file: {
                "format": "json", 
                "encoding": "utf8", 
                "indent": 4
            }
        }
    })
    process.crawl(TelegramSpider, start_url=url)
    process.start()

if __name__ == "__main__":
    # Usar argparse para permitir pasar el start_url desde la línea de comandos
    parser = argparse.ArgumentParser(description="Scrapy Telegram Spider")
    parser.add_argument("start_url", help="La URL de inicio para scrapeo")
    args = parser.parse_args()

    # Ejecutar spider pasando la URL
    run_spider(args.start_url)
