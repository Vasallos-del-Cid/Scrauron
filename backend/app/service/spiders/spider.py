import logging
import scrapy
from datetime import datetime
import re
import time
import random
from urllib.parse import urlparse
import json
from bson import ObjectId

from app.models.publicacion import Publicacion
from app.models.fuente import Fuente
from app.mongo.mongo_fuentes import get_fuente_by_id
from app.mongo.mongo_publicaciones import create_publicacion, update_publicacion
from app.mongo.mongo_utils import get_collection
from app.service.similarity_search.similarity_search import buscar_y_enlazar_a_conceptos, obtener_keywords_relacionadas
from app.service.llm.llm_utils import analizar_publicacion
from pymongo.errors import DuplicateKeyError, WriteError, ConnectionFailure

class NoticiasSpider(scrapy.Spider):
    name = "noticias"

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    def __init__(self, fuente_json=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not fuente_json:
            raise ValueError("Se requiere el parámetro 'fuente_json' con los datos de la fuente.")

        self.fuente = Fuente.from_dict(json.loads(fuente_json))
        self.start_urls = [self.fuente.url]

        self.total_guardados = 0
        self.total_ignorados = 0
        self.total_relacionados = 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.extraer_titular_noticias)

    def extraer_titular_noticias(self, response):
        titulos_baneados = {
            "Nacional", "Internacional", "Economía", "Opinión", "Tele",
            "Gente", "Deportes", "20bits", "Ed. Impresa", "España"
        }

        for noticia in response.xpath(self.fuente.etiqueta_titulo):
            texto = noticia.xpath(".//text()").getall()
            enlace = noticia.xpath("@href").get()

            if texto and enlace:
                texto_limpio = " ".join(t.strip() for t in texto if t.strip())

                if len(texto_limpio.split()) == 1 and texto_limpio.strip() in titulos_baneados:
                    logging.info(f"⛔ Título ignorado: '{texto_limpio}'")
                    continue

                if "h1" in self.fuente.etiqueta_titulo and len(texto_limpio.split()) <= 3:
                    continue

                url_completa = response.urljoin(enlace)

                if not url_completa.startswith(self.fuente.url):
                    logging.info(f"⛔ Ignorada URL fuera de dominio: {url_completa}")
                    continue

                if get_collection("publicaciones").find_one({"url": url_completa}):
                    logging.warning(f"⚠️ Ya existe en Mongo: {url_completa}")
                    self.total_ignorados += 1
                    continue

                yield scrapy.Request(
                    url_completa,
                    callback=self.extraer_contenido_noticia_nueva,
                    meta={
                        'titulo': texto_limpio,
                        'url': url_completa,
                        'fuente_id': self.fuente._id
                    }
                )

    def extraer_contenido_noticia_nueva(self, response):
        delay = random.uniform(0.5, 2)
        time.sleep(delay)

        logging.info(f"📰 Procesando noticia...")

        titulo = response.meta['titulo']
        url = response.meta['url']
        fuente_id = ObjectId(response.meta['fuente_id'])

        contenido = []
        for p in response.xpath(self.fuente.etiqueta_contenido):
            texto = " ".join(p.xpath(".//text()").getall()).strip()
            if len(texto.split()) > 20:
                contenido.append(texto)

        contenido_unido = " ".join(contenido)

        publicacion = Publicacion(
            titulo=titulo,
            url=url,
            fecha=datetime.now(),
            contenido=contenido_unido,
            fuente_id=fuente_id
        )

        fuente = get_fuente_by_id(fuente_id)

        try:
            logging.info(f"💾 Intentando guardar: {titulo[:60]}...")
            insert_result = create_publicacion(publicacion)
            publicacion._id = str(insert_result.inserted_id)

            self.total_guardados += 1
            logging.info(f"✅ Artículo guardado: {titulo} | Fuente: {fuente.nombre}")

            conceptos_enlazados_ids = buscar_y_enlazar_a_conceptos(publicacion)

            keywords_relacionadas = obtener_keywords_relacionadas(publicacion)
            if keywords_relacionadas:
                logging.info(f"🔗 Keywords relacionadas encontradas ({len(keywords_relacionadas)}):")
                for kw in keywords_relacionadas:
                    logging.info(f"🧠 {kw['nombre']} (similitud: {kw['similitud']})")
            else:
                logging.info("📭 No se encontraron keywords relacionadas con la publicación.")

            publicacion.keywords_relacionadas_ids = [ObjectId(k["keyword_id"]) for k in keywords_relacionadas]

            if conceptos_enlazados_ids:
                publicacion.conceptos_relacionados_ids = conceptos_enlazados_ids
                publicacion = analizar_publicacion(publicacion)
                self.total_relacionados += 1
            else:
                publicacion.contenido = ""

            update_publicacion(
                pub_id=publicacion._id,
                data={
                    "contenido": publicacion.contenido,
                    "tono": publicacion.tono,
                    "ciudad_region": str(publicacion.ciudad_region) if publicacion.ciudad_region else None,
                    "pais": str(publicacion.pais) if publicacion.pais else None,
                    "keywords_relacionadas_ids": publicacion.keywords_relacionadas_ids,
                    "conceptos_relacionados_ids": publicacion.conceptos_relacionados_ids
                },
            )
        except DuplicateKeyError:
            logging.warning(f"⚠️ Ya existe (aunque no se detectó antes): {url}")
        except ConnectionFailure:
            logging.error(f" ❌ No se pudo conectar a MongoDB.")
        except WriteError as e:
            logging.error(f" ❌ Error de escritura en MongoDB: {e}")
        except Exception as e:
            logging.error(f" ❌ Error inesperado: {e}")

        print("---------------------------------------------------------------------------------")

    def closed(self, reason):
        logging.info(f" 📦 Total guardados: {self.total_guardados}")
        logging.info(f" 🧠 Total relacionados: {self.total_relacionados}")
        logging.info(f" 🚫 Total ignorados (ya existentes): {self.total_ignorados}")
        print("---------------------------------------------------------------------------------")