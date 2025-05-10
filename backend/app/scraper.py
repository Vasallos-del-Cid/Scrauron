import logging
import subprocess
import sys
import os


# Ejecuta el script spider_executor.py como un subproceso externo de Python, pasando la url como argumento.
# Se lanza un subproceso para ejecutar el job de scraping sin bloquear el hilo principal.
""" @deprecated SE USA EL  SCRAPER DE SCRAPING_JOB
def ejecutar_scraping(url):
    logging.info("Ejecutando subproceso de scraping...")
    return subprocess.run(
        [sys.executable, "app/spiders/spider_executor.py", url],
        env=os.environ.copy(),  # pasa todas las vars actuales, incluyendo MONGO_URI
        check=True)
"""