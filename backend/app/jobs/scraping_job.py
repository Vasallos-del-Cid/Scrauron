import logging
import os
import sys
import time
import threading
import subprocess
import random
from datetime import datetime, timedelta

from app.mongo.mongo_utils import get_collection

# Frecuencia base para ejecutar scraping (en minutos)
SCRAPING_FREQ_MIN = 40  

# =========================
# Ejecuta el script spider_executor.py pasando la URL como argumento
# =========================
def ejecutar_scraping(url):
    logging.info(f" 🕷️ Ejecutando scraping para: {url}")
    try:
        # Ejecuta el spider como subproceso
        subprocess.run(
            [sys.executable, "app/spiders/spider_executor.py", url],
            env=os.environ.copy(),  # pasa todas las vars actuales, incluyendo MONGO_URI
            check=True  # Lanza excepción si el script falla
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Scraping falló con código {e.returncode}")
        raise RuntimeError(f"Error durante el scraping {e}")
    except Exception as e:
        logging.error(f"💥 Error ejecutando spider: {e}")
        raise RuntimeError(f"Error durante el scraping {e}")

# =========================
# Ejecuta scraping para todas las fuentes guardadas en MongoDB
# =========================
def scraping_todas_las_fuentes():
    fuentes = list(get_collection("fuentes").find())
    for fuente in fuentes:
        url = fuente.get("url")
        if url:
            ejecutar_scraping(url)

# =========================
# Bucle principal del scheduler: ejecuta el scraping cada X minutos con variación aleatoria
# =========================
def scheduler_loop():
    while True:
        hora_inicio = datetime.now().strftime('%H:%M:%S')
        logging.info(f"\n[{hora_inicio}] 🔁 Lanzando scraping de todas las fuentes...")
        
        # Ejecutar scraping de todas las fuentes
        scraping_todas_las_fuentes()
        
        # Variar el intervalo aleatoriamente entre -20% y +20%
        factor = random.uniform(0.8, 1.2)
        espera_min = SCRAPING_FREQ_MIN * factor
        espera_seg = espera_min * 60

        hora_siguiente = datetime.now() + timedelta(seconds=espera_seg)

        logging.info(f"🕒 Esperando {espera_min:.2f} minutos para la siguiente ejecución...")
        logging.info(f"🕒 Próxima ejecución a las {hora_siguiente.strftime('%H:%M:%S')}")

        # Pausar hasta la próxima ejecución
        time.sleep(espera_seg)

# =========================
# Lanza el scheduler en un hilo en segundo plano al iniciar la app
# =========================
def iniciar_scheduler_en_segundo_plano():
    hilo = threading.Thread(target=scheduler_loop, daemon=True)
    hilo.start()
