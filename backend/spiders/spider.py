import scrapy
from scrapy.crawler import CrawlerProcess
import os
import re
import json
from flask import Flask, jsonify, request


class NoticiasSpider(scrapy.Spider):
    custom_settings = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
    name = "noticias"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url] if url else ["https://www.elespanol.com/"]

    import scrapy

    def parse(self, response):
        print(response.text)

        # Caso 1: <h2><a>...</a></h2>
        for noticia in response.xpath("//h2/a"):
            texto = noticia.xpath(".//text()").getall()
            enlace = noticia.xpath("@href").get()
            if texto and enlace:
                url_completa = response.urljoin(enlace)
                yield scrapy.Request(url_completa, callback=self.parse_contenido, meta={'titulo': " ".join(t.strip() for t in texto if t.strip()), 'url': url_completa})

        # Caso 2: <a><h2>...</h2></a>
        for noticia in response.xpath("//a[h2]"):
            texto = noticia.xpath(".//h2//text()").getall()
            enlace = noticia.xpath("@href").get()
            if texto and enlace:
                url_completa = response.urljoin(enlace)
                yield scrapy.Request(url_completa, callback=self.parse_contenido, meta={'titulo': " ".join(t.strip() for t in texto if t.strip()), 'url': url_completa})

        # Caso 3: <h3><a>...</a></h3>
        for noticia in response.xpath("//h3/a"):
            texto = noticia.xpath(".//text()").getall()
            enlace = noticia.xpath("@href").get()
            if texto and enlace:
                url_completa = response.urljoin(enlace)
                yield scrapy.Request(url_completa, callback=self.parse_contenido, meta={'titulo': " ".join(t.strip() for t in texto if t.strip()), 'url': url_completa})

        # Caso 4: <a><h3>...</h3></a>
        for noticia in response.xpath("//a[h3]"):
            texto = noticia.xpath(".//h3//text()").getall()
            enlace = noticia.xpath("@href").get()
            if texto and enlace:
                url_completa = response.urljoin(enlace)
                yield scrapy.Request(url_completa, callback=self.parse_contenido, meta={'titulo': " ".join(t.strip() for t in texto if t.strip()), 'url': url_completa})

        # Caso 5: <h1><a>...</a></h1> (solo si tiene más de 3 palabras)
        for noticia in response.xpath("//h1/a"):
            texto = noticia.xpath(".//text()").getall()
            enlace = noticia.xpath("@href").get()
            # Contamos las palabras del texto y verificamos si tiene más de 3 palabras
            if texto and enlace:
                texto_limpio = " ".join(t.strip() for t in texto if t.strip())
                if len(texto_limpio.split()) > 3:
                    url_completa = response.urljoin(enlace)
                    yield scrapy.Request(url_completa, callback=self.parse_contenido, meta={'titulo': texto_limpio, 'url': url_completa})

        # Caso 6: <a><h1>...</h1></a> (solo si tiene más de 3 palabras)
        for noticia in response.xpath("//a[h1]"):
            texto = noticia.xpath(".//h1//text()").getall()
            enlace = noticia.xpath("@href").get()
            # Contamos las palabras del texto y verificamos si tiene más de 3 palabras
            if texto and enlace:
                texto_limpio = " ".join(t.strip() for t in texto if t.strip())
                if len(texto_limpio.split()) > 3:
                    url_completa = response.urljoin(enlace)
                    yield scrapy.Request(url_completa, callback=self.parse_contenido, meta={'titulo': texto_limpio, 'url': url_completa})

    def parse_contenido(self, response):
        # Extraer el título y la URL desde los metadatos
        titulo = response.meta['titulo']
        url = response.meta['url']

        # Extraer todos los párrafos (<p>) con más de 20 palabras
        contenido = []
        for p in response.xpath("//p"):
            texto = " ".join(p.xpath(".//text()").getall()).strip()
            if len(texto.split()) > 20:
                contenido.append(texto)

        # Unir los textos de todos los párrafos seleccionados en una sola cadena
        contenido_unido = " ".join(contenido)

        # Guardar los datos extraídos (título, URL, contenido)
        yield {
            "titulo": titulo,
            "url": url,
            "contenido": contenido_unido
        }



#Obtener el nombre del sitio web. Texto entre www. y .com o .es
def obtener_nombre_archivo(url):
    match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9\-]+)\.(com|es)', url)
    if match:
        dominio = match.group(1)
    else:
        dominio = "sitio"
    return f"resultados_{dominio}.json"

# Flask setup
app = Flask(__name__)

def ejecutar_scraping(url):
    nombre_archivo = obtener_nombre_archivo(url)

    # Obtener la ruta del directorio donde se encuentra el script
    script_dir = os.path.dirname(__file__)
    
    # Crear una ruta relativa al directorio 'json' que está en la raíz del proyecto
    carpeta_salida = os.path.join(script_dir, "..", "json")  # Subimos un nivel desde 'spiders' y accedemos a 'json'
    
    # Asegurarnos de que la carpeta 'json' exista
    os.makedirs(carpeta_salida, exist_ok=True)

    # Crear la ruta completa para el archivo de salida
    ruta_salida = os.path.join(carpeta_salida, nombre_archivo)

    # Eliminar el archivo anterior si ya existe
    if os.path.exists(ruta_salida):
        os.remove(ruta_salida)

    # Configurar y ejecutar el proceso de Scrapy
    process = CrawlerProcess(settings={
        "FEEDS": {
            ruta_salida: {"format": "json", "encoding": "utf8", "indent": 4}
        },
        "LOG_ENABLED": True
    })
    process.crawl(NoticiasSpider, url=url)
    process.start()

    # Leer el archivo generado
    with open(ruta_salida, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data