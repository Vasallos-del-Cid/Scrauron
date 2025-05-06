import scrapy
from scrapy_playwright.page import PageMethod
import hashlib
from datetime import datetime
import re
from app.mongo.mongo_publicaciones import get_mongo_collection
from pymongo.errors import DuplicateKeyError, ConnectionFailure, WriteError
from app.models.publicacion import Publicacion

coleccion = get_mongo_collection()

class TelegramSpider(scrapy.Spider):
    name = "telegram"

    custom_settings = {
        # 1. Usa el navegador Chromium
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        # 2. Lanza el navegador en modo "headless" (sin interfaz gráfica)
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        # 3. Cambia el gestor de descargas para usar Playwright en vez de Scrapy normal
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        # 4. Cambia el reactor de eventos para compatibilidad con asyncio
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        # 5. Tiempo máximo de navegación por página (60 segundos)
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60 * 1000,
    }

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("TelegramSpider inicializado con:", url)
        self.start_urls = [url] if url else [""]
        self.fuente = self.start_urls[0]

    #Renderizar la página para capturarla despues de ejecucion de javascript (Playwright)
    def start_requests(self):
        print("📡 Ejecutando start_requests()")
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        #Espera a que se cargue el contenido de Telegram
                        PageMethod("wait_for_selector", "div.tgme_widget_message_text", timeout=30000),
                        #espera adicional de 5 segundos (por si aún está cargando).
                        PageMethod("wait_for_timeout", 5000),
                        #Toma una captura de pantalla de la página para depuración.
                        PageMethod("screenshot", path="app/spiders/debug/debug_telegram.png", full_page=True),
                    ],
                },
                callback=self.extraer_publicacion_telegram,
                errback=self.handle_error
            )
    #Gestion de errores
    def handle_error(self, failure):
        self.logger.error("ERROR en la solicitud:")
        self.logger.error(repr(failure))

    #Del HTML principal extraer todos los titulares y contenido. En Telegram son lo mismo (Titulo = primera frase del contenido)
    def extraer_publicaciones_telegram(self, response):
        print("Entró en extraer_publicaciones_telegram():", response.url)
        #Guardar el html de la fuente para debug
        with open("app/spiders/debug/debug_telegram.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        mensajes = response.css("div.tgme_widget_message_text")
        print(f"Mensajes encontrados: {len(mensajes)}")

        total_guardados = 0

        for msg in mensajes:
            contenido = msg.xpath("string()").get().strip()
            if not contenido or len(contenido) < 10:
                continue

            match = re.match(r"^(.*?[.!?])(\s|$)", contenido)
            titulo = match.group(1).strip() if match else contenido[:60]

            hash_id = hashlib.sha1((self.fuente + contenido).encode("utf-8")).hexdigest()

            publicacion = Publicacion(
                titulo=titulo,
                url=self.fuente,
                fecha=datetime.now(),
                contenido=contenido,
                fuente=self.fuente
            )
            publicacion._id = hash_id
            #Guardado en BBDD
            try:
                coleccion.insert_one(publicacion.to_dict())
                total_guardados += 1
                print(f"✅ Artículo guardado: {titulo} | Fuente: {publicacion.fuente}")
            except DuplicateKeyError:
                print("❌ Ya existe un artículo con esa clave.")
            except ConnectionFailure:
                print("❌ No se pudo conectar a MongoDB.")
            except WriteError as e:
                print(f"❌ Error al escribir en la base de datos: {e}")
            except Exception as e:
                print(f"❌ Error inesperado: {e}")

        print(f"\n💾 Total guardados: {total_guardados}")
