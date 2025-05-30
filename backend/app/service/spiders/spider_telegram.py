import logging

import scrapy
from scrapy_playwright.page import PageMethod
from datetime import datetime
from pymongo.errors import DuplicateKeyError, ConnectionFailure, WriteError
from app.mongo.mongo_publicaciones import create_publicacion
from app.models.publicacion import Publicacion
from app.service.similarity_search.similarity_search import buscar_y_enlazar_a_conceptos
import re


# Spider especializado para scraping de páginas similares a Telegram
class TelegramSpider(scrapy.Spider):
    name = "telegram"

    # Configuración para usar Playwright con Scrapy
    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60 * 1000,
    }

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url] if url else [""]
        self.fuente = self.start_urls[0]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "article.cpost-wt-text", timeout=30000),
                        PageMethod("wait_for_timeout", 5000),
                        PageMethod("screenshot", path="app/spiders/debug/debug_telegram.png", full_page=True),
                    ],
                },
                callback=self.extraer_publicacion_telegram,
                errback=self.handle_error
            )

    def handle_error(self, failure):
        self.logger.error("ERROR en la solicitud:")
        self.logger.error(repr(failure))



    def extraer_publicacion_telegram(self, response):
        logging.info("Entró en extraer_publicacion_telegram():", response.url)

        # Guarda el HTML para debug
        with open("app/spiders/debug/debug_telegram.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        # Selecciona todos los artículos visibles en la página
        articulos = response.css("article.cpost-wt-text")
        logging.info(f"Artículos encontrados: {len(articulos)}")

        total_guardados = 0

        for articulo in articulos:
            # Extrae todo el contenido de texto del artículo (sin etiquetas)
            texto_completo = articulo.xpath("string()").get(default="").strip()

            # Omite artículos vacíos o demasiado cortos
            if not texto_completo or len(texto_completo) < 10:
                continue

            # Elimina cualquier URL del texto
            texto_limpio = re.sub(r'https?://\S+|www\.\S+', '', texto_completo).strip()

            # Título: si empieza con <b> úsalo, si no, toma primera frase
            titulo = ""
            if articulo.css("b::text"):
                titulo = articulo.css("b::text").get().strip()
            else:
                match = re.match(r"^(.*?[.!?])(\s|$)", texto_limpio)
                titulo = match.group(1).strip() if match else texto_limpio[:60]

            # Crea objeto Publicación
            publicacion = Publicacion(
                titulo=titulo,
                url=self.fuente,
                fecha=datetime.now(),
                contenido=texto_limpio,
                fuente=self.fuente
            )

            try:
                # Intenta guardar en MongoDB
                insert_result = create_publicacion(publicacion)
                if insert_result:
                    publicacion._id = str(insert_result.inserted_id)
                    total_guardados += 1
                    logging.info(f"✅ Artículo guardado: {titulo} | Fuente: {publicacion.fuente}")

                    # Enlaza con conceptos relacionados
                    buscar_y_enlazar_a_conceptos(publicacion)
                else:
                    logging.warning("⚠️ No se insertó (posiblemente duplicado).")

            except DuplicateKeyError:
                logging.error("❌ Ya existe un artículo con esa clave.")
            except ConnectionFailure:
                logging.error("❌ No se pudo conectar a MongoDB.")
            except WriteError as e:
                logging.error(f"❌ Error al escribir en la base de datos: {e}")
            except Exception as e:
                logging.error(f"❌ Error inesperado: {e}")

            print("---------------------------------------------------------------------------------")

        logging.info(f"\n💾 Total guardados: {total_guardados}")

