import logging
import sys
import os
import json
from scrapy.crawler import CrawlerProcess

# Añadir la ruta del proyecto al sys.path para importar módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Importaciones internas
from app.config import logqing_config
from app.service.spiders.spider import NoticiasSpider
from app.service.spiders.spider_telegram import TelegramSpider
from app.mongo.mongo_utils import init_mongo
from app.models.fuente import Fuente

# Inicializar conexión a MongoDB y logging
init_mongo()
logqing_config()

# Verificar argumentos
if len(sys.argv) < 2:
    print("❌ Debes pasar un objeto Fuente serializado en JSON como argumento.")
    sys.exit(1)

# Obtener fuente_json del argumento
fuente_json = sys.argv[1]

# Intentar cargar la fuente
try:
    fuente_dict = json.loads(fuente_json)
    fuente = Fuente.from_dict(fuente_dict)
except Exception as e:
    print(f"❌ Error interpretando fuente: {e}")
    sys.exit(1)

# Configuración y ejecución de Scrapy
process = CrawlerProcess(settings={
    "LOG_ENABLED": False
})

# Elegir spider en función del tipo de URL
if fuente.url.startswith(("https://tlgrm", "http://tlgrm", "https://t.me", "http://t.me")):
    logging.info("📲 Fuente Telegram detectada. Usando TelegramSpider.")
    process.crawl(TelegramSpider, fuente_json=fuente_json)
else:
    logging.info("🌐 Fuente de noticia detectada. Usando NoticiasSpider.")
    process.crawl(NoticiasSpider, fuente_json=fuente_json)

# Iniciar proceso
process.start()
