import logging
import sys
import os
from scrapy.crawler import CrawlerProcess

# Añadir la ruta del proyecto al sys.path para importar módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# mantener el orden de los imports
from app.config import logqing_config
from app.spiders.spider import NoticiasSpider
from app.spiders.spider_telegram import TelegramSpider
from app.mongo.mongo_utils import init_mongo

# Se debe inicializar la conexión a MongoDB tambien en el subproceso
init_mongo()
logqing_config()

if len(sys.argv) < 2:
    sys.exit(1)
# recibir url como argumento
url = sys.argv[1]

# Configuración y ejecución de Scrapy
process = CrawlerProcess(settings={
    "LOG_ENABLED": False
})

# Si es una url de Telegram usar TelegramSpider, sino usar NoticiasSpider
if url.startswith(("https://tlgrm", "http://tlgrm")):
    logging.info("Detectado Telegram. Usando TelegramSpider.")
    process.crawl(TelegramSpider, url=url)
else:
    logging.info("Detectada URL de noticia. Usando NoticiasSpider.")
    process.crawl(NoticiasSpider, url=url)

process.start()
