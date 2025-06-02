import json
import logging
import os
import sys
import time
import threading
import subprocess
import random
from datetime import datetime, timedelta
from app.mongo.mongo_utils import get_collection
from app.models.fuente import Fuente

# Frecuencia base para ejecutar scraping (en minutos)
SCRAPING_FREQ_MIN = os.getenv("SCRAPING_FREQUENCY", 40)
detener_flag = threading.Event()

# =========================
# Ejecuta el script spider_executor.py pasando la URL como argumento
# =========================
def ejecutar_scraping(fuente: Fuente):
    """
    Ejecuta el proceso de scraping para una instancia de Fuente.
    """
    logging.info(f" 🕷️ Ejecutando scraping para: {fuente.nombre} ({fuente.url})")
    fuente_json = json.dumps(fuente.to_dict())
    try:
        subprocess.run(
            [sys.executable, "app/service/spiders/spider_executor.py", fuente_json],
            env=os.environ.copy(),
            check=True,
            timeout=1200  # Si tarda más de 20 minutos, se aborta
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Scraping falló con código {e.returncode}")
        raise RuntimeError(f"Error durante el scraping para {fuente.url} - Código: {e.returncode}")
    except Exception as e:
        logging.error(f"💥 Error ejecutando spider: {e}")
        raise RuntimeError(f"Error durante el scraping para {fuente.url}: {e}")


# =========================
# Ejecuta scraping para todas las fuentes guardadas en MongoDB
# =========================
def scraping_todas_las_fuentes():
    fuentes = list(get_collection("fuentes").find())
    for fuente_dict in fuentes:
        if detener_flag.is_set():
            logging.info("🛑 Detención solicitada. Cancelando scraping de fuentes.")
            break
        fuente = Fuente.from_dict(fuente_dict)
        ejecutar_scraping(fuente)

# =========================
# Bucle principal del scheduler: ejecuta el scraping cada X minutos con variación aleatoria
# =========================
def scheduler_loop():
    while not detener_flag.is_set():
        logging.info("🔁 Lanzando scraping de todas las fuentes...")
        scraping_todas_las_fuentes()
        # factor = random.uniform(0.8, 1.2)
        # espera_min = SCRAPING_FREQ_MIN * factor
        # espera_seg = espera_min * 40
        espera_min = float(SCRAPING_FREQ_MIN)
        espera_seg = espera_min * 60
        hora_siguiente = datetime.now() + timedelta(seconds=espera_seg)
        logging.info(f"🕒 Esperando {espera_min:.2f} minutos para la siguiente ejecución...")
        logging.info(f"🕒 Próxima ejecución a las {hora_siguiente.strftime('%H:%M:%S')}")
        # Espera con interrupción controlada
        if detener_flag.wait(timeout=espera_seg):
            logging.info("🛑 Scheduler detenido durante la espera.")
            break
    logging.info("🎯 Scheduler finalizado.")

# =========================
# Lanza el scheduler en un hilo en segundo plano al iniciar la app
# =========================
def iniciar_scheduler_en_segundo_plano():
    detener_flag.clear()
    hilo = threading.Thread(target=scheduler_loop, daemon=True)
    hilo.start()


def detener_scheduler():
    detener_flag.set()
    logging.info("🛑 Señal enviada para detener el scheduler.")
