# Spider de Scrapy para extraer titulares y contenidos de noticias, guardarlos en MongoDB
# y enlazarlos semánticamente con conceptos registrados usando FAISS.

import scrapy
from datetime import datetime
import re
import time
import random
from urllib.parse import urlparse

# Funciones de acceso a Mongo y modelo de datos
from app.mongo.mongo_publicaciones import get_mongo_collection, create_publicacion, update_publicacion
from pymongo.errors import DuplicateKeyError, WriteError, ConnectionFailure
from app.models.publicacion import Publicacion
from app.similarity_search.similarity_search import buscar_y_enlazar_a_conceptos
from app.llm.llm_utils import resumir_contenido_reformulado

# Establece conexión con la colección Mongo de publicaciones
coleccion = get_mongo_collection()

# Extrae nombre base y dominio completo a partir de una URL
def extraer_fuente_info(url):
    dominio_completo = urlparse(url).netloc
    nombre_base_match = re.match(r"(?:www\.)?([^\.]+)", dominio_completo)
    nombre_base = nombre_base_match.group(1) if nombre_base_match else dominio_completo
    return nombre_base, dominio_completo

# Define la clase principal del spider
class NoticiasSpider(scrapy.Spider):
    # Define un User-Agent personalizado para evitar bloqueos por scraping
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    name = "noticias"

    # Inicializa el spider con la URL de entrada
    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url] if url else [""]
        self.total_guardados = 0
        self.total_ignorados = 0

    # Lanza la primera petición HTTP para cada URL inicial
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.extraer_titular_noticias)

    # Extrae los titulares desde la página inicial (h1, h2 con enlaces)
    def extraer_titular_noticias(self, response):
        fuente_nombre, fuente_dominio = extraer_fuente_info(response.url)

        # Lista de títulos genéricos que se deben ignorar
        titulos_baneados = {
            "Nacional", "Internacional", "Economía", "Opinión", "Tele",
            "Gente", "Deportes", "20bits", "Ed. Impresa"
        }

        # Busca enlaces a noticias en varios formatos posibles
        for xpath in ["//h2/a", "//a[h2]", "//h1/a", "//a[h1]"]:
            for noticia in response.xpath(xpath):
                texto = noticia.xpath(".//text()").getall()
                enlace = noticia.xpath("@href").get()

                if texto and enlace:
                    texto_limpio = " ".join(t.strip() for t in texto if t.strip())

                    # Ignora encabezados genéricos sin contenido informativo
                    if len(texto_limpio.split()) == 1 and texto_limpio.strip() in titulos_baneados:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⛔ Título ignorado: '{texto_limpio}'")
                        continue

                    # Filtra h1s demasiado cortos
                    if "h1" in xpath and len(texto_limpio.split()) <= 3:
                        continue

                    # Construye URL completa
                    url_completa = response.urljoin(enlace)

                    # Verifica si ya existe en Mongo para evitar duplicados
                    if coleccion.find_one({"url": url_completa}):
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ya existe en Mongo: {url_completa}")
                        self.total_ignorados += 1
                        continue

                    # Lanza nueva petición para extraer el contenido completo
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

    # Extrae el contenido completo de la noticia desde su página
    def extraer_contenido_noticia_nueva(self, response):
        # Simula un retraso aleatorio para no sobrecargar el servidor
        delay = random.uniform(1, 5)
        time.sleep(delay)

        hora_inicio = datetime.now().strftime('%H:%M:%S')
        print(f"[{hora_inicio}] 📰 Procesando noticia...")

        # Recupera los metadatos guardados
        titulo = response.meta['titulo']
        url = response.meta['url']
        fuente_nombre = response.meta['fuente_nombre']
        fuente_dominio = response.meta['fuente_dominio']

        # Extrae todos los <p> y guarda los suficientemente largos
        contenido = []
        for p in response.xpath("//p"):
            texto = " ".join(p.xpath(".//text()").getall()).strip()
            if len(texto.split()) > 20:
                contenido.append(texto)

        contenido_unido = " ".join(contenido)

        # Construye objeto Publicacion para guardar en Mongo
        publicacion = Publicacion(
            titulo=titulo,
            url=url,
            fecha=datetime.now(),
            contenido=contenido_unido,
            fuente=fuente_dominio
        )

        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 💾 Intentando guardar: {titulo[:60]}...")

            # Inserta en MongoDB
            insert_result = create_publicacion(publicacion)
            publicacion._id = str(insert_result.inserted_id)  # Asigna ID real

            self.total_guardados += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Artículo guardado: {titulo} | Fuente: {fuente_nombre} ({fuente_dominio})")

            # Busca conceptos semánticamente relacionados y asocia la publicación
            buscar_y_enlazar_a_conceptos(publicacion)

            publicacion = resumir_contenido_reformulado(publicacion)

            update_publicacion(
                pub_id=publicacion._id,
                data={"contenido": publicacion.contenido}
            )

            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Contenido resumido: {publicacion.contenido}")
        # Manejo de errores específicos de Mongo
        except DuplicateKeyError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ya existe (aunque no se detectó antes): {url}")
        except ConnectionFailure:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ No se pudo conectar a MongoDB.")
        except WriteError as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error de escritura en MongoDB: {e}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error inesperado: {e}")

        print("---------------------------------------------------------------------------------")

    # Se ejecuta al finalizar el spider e imprime estadísticas
    def closed(self, reason):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📦 Total guardados: {self.total_guardados}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚫 Total ignorados (ya existentes): {self.total_ignorados}")
        print("---------------------------------------------------------------------------------")
