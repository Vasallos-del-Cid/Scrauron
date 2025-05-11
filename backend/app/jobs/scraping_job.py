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

scheduler_thread = None
detener_flag = threading.Event()

# =========================
# Ejecuta el script spider_executor.py pasando la URL como argumento
# =========================
def ejecutar_scraping(url):
    logging.info(f" 🕷️ Ejecutando scraping para: {url}")
    try:
        subprocess.run(
            [sys.executable, "app/spiders/spider_executor.py", url],
            env=os.environ.copy(),
            check=True,
            timeout=1200 #Si tarda mas de 20 minutos en una fuente aborta
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
        if detener_flag.is_set():
            logging.info("🛑 Detención solicitada. Cancelando scraping de fuentes.")
            break
        url = fuente.get("url")
        if url:
            ejecutar_scraping(url)

# =========================
# Bucle principal del scheduler: ejecuta el scraping cada X minutos con variación aleatoria
# =========================
def scheduler_loop():
    while not detener_flag.is_set():
        logging.info(f"🔁 Lanzando scraping de todas las fuentes...")
        
        scraping_todas_las_fuentes()

        factor = random.uniform(0.8, 1.2)
        espera_min = SCRAPING_FREQ_MIN * factor
        espera_seg = espera_min * 60

        hora_siguiente = datetime.now() + timedelta(seconds=espera_seg)

        logging.info(f"🕒 Esperando {espera_min:.2f} minutos para la siguiente ejecución...")
        logging.info(f"🕒 Próxima ejecución a las {hora_siguiente.strftime('%H:%M:%S')}")

        # Esperar pero permitir interrupción si se activa el flag
        if detener_flag.wait(timeout=espera_seg):
            logging.info("🛑 Scheduler detenido durante la espera.")
            break

    logging.info("🎯 Scheduler finalizado.")

# =========================
# Lanza el scheduler en un hilo en segundo plano al iniciar la app
# =========================
def iniciar_scheduler_en_segundo_plano():
    global scheduler_thread
    if scheduler_thread is None or not scheduler_thread.is_alive():
        logging.info("🚀 Iniciando scheduler en segundo plano...")
        detener_flag.clear()
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
    else:
        logging.info("⚠️ Scheduler ya está en ejecución.")

def detener_scheduler():
    logging.info("⛔ Solicitando detener scheduler...")
    detener_flag.set()
    # No usar join aquí directamente, solo si estás seguro de que no es el hilo Flask
    logging.info("📤 Señal enviada para detener el scheduler.")
