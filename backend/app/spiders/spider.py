import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime
import re
from urllib.parse import urlparse
from app.mongo.mongo_publicaciones import get_mongo_collection
from pymongo.errors import DuplicateKeyError, WriteError, ConnectionFailure
from app.models.publicacion import Publicacion

coleccion = get_mongo_collection()

def extraer_fuente_info(url):
    dominio_completo = urlparse(url).netloc
    nombre_base_match = re.match(r"(?:www\.)?([^\.]+)", dominio_completo)
    nombre_base = nombre_base_match.group(1) if nombre_base_match else dominio_completo
    return nombre_base, dominio_completo

class NoticiasSpider(scrapy.Spider):
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    name = "noticias"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url] if url else ["https://www.elespanol.com/"]
        self.total_guardados = 0

    def parse(self, response):
        fuente_nombre, fuente_dominio = extraer_fuente_info(response.url)

        for xpath in ["//h2/a", "//a[h2]", "//h3/a", "//a[h3]", "//h1/a", "//a[h1]"]:
            for noticia in response.xpath(xpath):
                texto = noticia.xpath(".//text()").getall()
                enlace = noticia.xpath("@href").get()
                if texto and enlace:
                    texto_limpio = " ".join(t.strip() for t in texto if t.strip())
                    if "h1" in xpath and len(texto_limpio.split()) <= 3:
                        continue
                    url_completa = response.urljoin(enlace)
                    yield scrapy.Request(url_completa, callback=self.parse_contenido, meta={
                        'titulo': texto_limpio,
                        'url': url_completa,
                        'fuente_nombre': fuente_nombre,
                        'fuente_dominio': fuente_dominio
                    })

    def parse_contenido(self, response):
        titulo = response.meta['titulo']
        url = response.meta['url']
        fuente_nombre = response.meta['fuente_nombre']
        fuente_dominio = response.meta['fuente_dominio']

        contenido = []
        for p in response.xpath("//p"):
            texto = " ".join(p.xpath(".//text()").getall()).strip()
            if len(texto.split()) > 20:
                contenido.append(texto)

        contenido_unido = " ".join(contenido)

        publicacion = Publicacion(
            titulo=titulo,
            url=url,
            fecha=datetime.now(),
            contenido=contenido_unido,
            fuente=fuente_dominio
        )

        try:
            coleccion.insert_one(publicacion.to_dict())
            self.total_guardados += 1
            print(f"✅ Artículo guardado: {titulo} | Fuente: {fuente_nombre} ({fuente_dominio})")
        except DuplicateKeyError:
            print("⚠️ Ya existe un artículo con esa clave.")
        except ConnectionFailure:
            print("❌ No se pudo conectar a MongoDB.")
        except WriteError as e:
            print(f"❌ Error al escribir en la base de datos: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

    def closed(self, reason):
        print(f"\n💾 Total guardados: {self.total_guardados}")

def obtener_nombre_archivo(url):
    match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9\-]+)\.(com|es)', url)
    if match:
        dominio = match.group(1)
    else:
        dominio = "sitio"
    return f"resultados_{dominio}.json"
