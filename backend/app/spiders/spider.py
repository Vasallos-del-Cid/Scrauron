import scrapy
from datetime import datetime
import re
import time
import random
from urllib.parse import urlparse
from app.mongo.mongo_publicaciones import get_mongo_collection
from pymongo.errors import DuplicateKeyError, WriteError, ConnectionFailure
from app.models.publicacion import Publicacion
from app.similarity_search.similarity_search import buscar_y_enlazar_a_conceptos

# Conexión a MongoDB
coleccion = get_mongo_collection()

# Extraer el nombre de la fuente desde la URL
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
        self.start_urls = [url] if url else [""]
        self.total_guardados = 0
        self.total_ignorados = 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.extraer_titular_noticias)

    def extraer_titular_noticias(self, response):
        fuente_nombre, fuente_dominio = extraer_fuente_info(response.url)

        # Títulos irrelevantes
        titulos_baneados = {
            "Nacional", "Internacional", "Economía", "Opinión", "Tele",
            "Gente", "Deportes", "20bits", "Ed. Impresa"
        }

        for xpath in ["//h2/a", "//a[h2]", "//h1/a", "//a[h1]"]:
            for noticia in response.xpath(xpath):
                texto = noticia.xpath(".//text()").getall()
                enlace = noticia.xpath("@href").get()

                if texto and enlace:
                    texto_limpio = " ".join(t.strip() for t in texto if t.strip())

                    if len(texto_limpio.split()) == 1 and texto_limpio.strip() in titulos_baneados:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⛔ Título ignorado: '{texto_limpio}'")
                        continue

                    if "h1" in xpath and len(texto_limpio.split()) <= 3:
                        continue

                    url_completa = response.urljoin(enlace)

                    if coleccion.find_one({"url": url_completa}):
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ya existe en Mongo: {url_completa}")
                        self.total_ignorados += 1
                        continue

                    yield scrapy.Request(
                        url_completa,
                        callback=self.extraer_contenido_noticia_nueva,
                        meta={
                            'titulo': texto_limpio,
                            'url': url_completa,
                            'fuente_nombre': fuente_nombre,
                            'fuente_dominio': fuente_dominio
                        }
                    )

    def extraer_contenido_noticia_nueva(self, response):
        delay = random.uniform(1, 5)
        time.sleep(delay)

        hora_inicio = datetime.now().strftime('%H:%M:%S')
        print(f"[{hora_inicio}] 📰 Procesando noticia...")

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
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 💾 Intentando guardar: {titulo[:60]}...")
            
            # Insertar en Mongo y asignar el _id generado
            insert_result = coleccion.insert_one(publicacion.to_dict())
            publicacion._id = str(insert_result.inserted_id)  # ✅ Asignar el _id real

            self.total_guardados += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Artículo guardado: {titulo} | Fuente: {fuente_nombre} ({fuente_dominio})")

            # Buscar conceptos similares y enlazar la publicación
            buscar_y_enlazar_a_conceptos(publicacion)

        except DuplicateKeyError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ya existe (aunque no se detectó antes): {url}")
        except ConnectionFailure:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ No se pudo conectar a MongoDB.")
        except WriteError as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error de escritura en MongoDB: {e}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error inesperado: {e}")

        print("---------------------------------------------------------------------------------")
        
    def closed(self, reason):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📦 Total guardados: {self.total_guardados}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚫 Total ignorados (ya existentes): {self.total_ignorados}")
        print("---------------------------------------------------------------------------------")
