import sys
import os
from scrapy.crawler import CrawlerProcess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.spiders.spider import NoticiasSpider  
from app.spiders.spider_telegram import TelegramSpider

if len(sys.argv) < 2:
    sys.exit(1)
#recibir url como argumento
url = sys.argv[1]

# Configuración y ejecución de Scrapy
process = CrawlerProcess(settings={
    "LOG_ENABLED": False  
})

#Si es una url de Telegram usar TelegramSpider, sino usar NoticiasSpider
if url.startswith(("https://t.me/", "http://t.me/")):
    print("Detectado Telegram. Usando TelegramSpider.")
    process.crawl(TelegramSpider, url=url)
else:
    print("Detectada URL de noticia. Usando NoticiasSpider.")
    process.crawl(NoticiasSpider, url=url)

process.start()
