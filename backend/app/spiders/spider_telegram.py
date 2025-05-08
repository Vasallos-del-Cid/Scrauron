# Spider que accede a canales de Telegram vía navegador automatizado con Playwright,
# extrae mensajes visibles, los guarda como publicaciones en MongoDB
# y captura el HTML renderizado para depuración.

import scrapy
from scrapy_playwright.page import PageMethod
import hashlib
from datetime import datetime
import re
from app.mongo.mongo_publicaciones import get_mongo_collection, create_publicacion
from pymongo.errors import DuplicateKeyError, ConnectionFailure, WriteError
from app.models.publicacion import Publicacion

# Se conecta a la colección de publicaciones en MongoDB
coleccion = get_mongo_collection()

# Spider especializado para Telegram usando Playwright para renderizar JavaScript
class TelegramSpider(scrapy.Spider):
    name = "telegram"

    # Configuración de Scrapy + Playwright para navegar con Chromium sin interfaz gráfica
    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",  # Usa el navegador Chromium
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},  # Sin interfaz
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",  # Reactor compatible con async
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60 * 1000,  # Timeout de 60s
    }

    # Constructor que recibe la URL del canal de Telegram
    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("TelegramSpider inicializado con:", url)
        self.start_urls = [url] if url else [""]
        self.fuente = self.start_urls[0]

    # Inicia la navegación y espera que el contenido se renderice antes de continuar
    def start_requests(self):
        print("📡 Ejecutando start_requests()")
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # Usa Playwright
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        # Espera que los mensajes se carguen
                        PageMethod("wait_for_selector", "div.tgme_widget_message_text", timeout=30000),
                        # Espera extra de 5 segundos para asegurar carga completa
                        PageMethod("wait_for_timeout", 5000),
                        # Captura screenshot para debug visual
                        PageMethod("screenshot", path="app/spiders/debug/debug_telegram.png", full_page=True),
                    ],
                },
                callback=self.extraer_publicacion_telegram,
                errback=self.handle_error
            )

    # Manejador de errores en la solicitud
    def handle_error(self, failure):
        self.logger.error("ERROR en la solicitud:")
        self.logger.error(repr(failure))

    # Extrae todos los mensajes de la página de Telegram ya renderizada
    def extraer_publicacion_telegram(self, response):
        print("Entró en extraer_publicaciones_telegram():", response.url)

        # Guarda el HTML para debug
        with open("app/spiders/debug/debug_telegram.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        # Selecciona los mensajes del canal
        mensajes = response.css("div.tgme_widget_message_text")
        print(f"Mensajes encontrados: {len(mensajes)}")

        total_guardados = 0

        for msg in mensajes:
            contenido = msg.xpath("string()").get().strip()
            if not contenido or len(contenido) < 10:
                continue

            # Usa la primera frase como título si es posible
            match = re.match(r"^(.*?[.!?])(\s|$)", contenido)
            titulo = match.group(1).strip() if match else contenido[:60]

            # Crea hash único como ID para evitar duplicados
            hash_id = hashlib.sha1((self.fuente + contenido).encode("utf-8")).hexdigest()

            # Crea el objeto Publicación con los datos del mensaje
            publicacion = Publicacion(
                titulo=titulo,
                url=self.fuente,
                fecha=datetime.now(),
                contenido=contenido,
                fuente=self.fuente
            )
            publicacion._id = hash_id

            # Intenta guardar la publicación en MongoDB
            try:
                create_publicacion(publicacion)
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
