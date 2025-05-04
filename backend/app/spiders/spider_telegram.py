import scrapy
from scrapy_playwright.page import PageMethod
import hashlib
from datetime import datetime
import re
from app.mongo.mongo_utils import get_mongo_collection
from pymongo.errors import DuplicateKeyError
from app.models.publicacion import Publicacion

coleccion = get_mongo_collection()

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
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60 * 1000,
    }

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("🚀 TelegramSpider inicializado con:", url)
        self.start_urls = [url] if url else ["https://t.me/s/Alviseperez"]
        self.fuente = self.start_urls[0]

    def start_requests(self):
        print("📡 Ejecutando start_requests()")
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.tgme_widget_message_text", timeout=30000),
                        PageMethod("wait_for_timeout", 5000),
                        #Guardar la imagen de la fuente para debug
                        PageMethod("screenshot", path="app/spiders/debug/debug_telegram.png", full_page=True),
                    ],
                },
                callback=self.parse,
                errback=self.handle_error
            )

    def handle_error(self, failure):
        self.logger.error("❌ ERROR en la solicitud:")
        self.logger.error(repr(failure))

    def parse(self, response):
        print("✅ Entró en parse():", response.url)
        #Guardar el html de la fuente para debug
        with open("app/spiders/debug/debug_telegram.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        mensajes = response.css("div.tgme_widget_message_text")
        print(f"📦 Mensajes encontrados: {len(mensajes)}")

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

            try:
                coleccion.insert_one(publicacion.to_dict())
                print(f"✅ Guardado: {titulo}")
                total_guardados += 1
            except DuplicateKeyError:
                print("⚠️ Ya existe este mensaje.")
            except Exception as e:
                print(f"❌ Error al guardar: {e}")

        print(f"\n💾 Total guardados: {total_guardados}")
