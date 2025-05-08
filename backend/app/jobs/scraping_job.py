import time
import threading
import subprocess
import random
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import ObjectId
from datetime import datetime, timedelta
from subprocess import TimeoutExpired

# =========================
# Cargar configuración del entorno (.env)
# =========================
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["baseDatosScrauron"]
coleccion_fuentes = db["fuentes"]

# Frecuencia base para ejecutar scraping (en minutos)
SCRAPING_FREQ_MIN = 40  

# =========================
# Ejecuta el script spider_executor.py pasando la URL como argumento
# =========================
def ejecutar_scraping(url):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🕷️ Ejecutando scraping para: {url}")
    try:
        # Ejecuta el spider como subproceso
        subprocess.run(
            ["python", "app/spiders/spider_executor.py", url],
            check=True  # Lanza excepción si el script falla
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraping falló con código {e.returncode}")
    except Exception as e:
        print(f"💥 Error ejecutando spider: {e}")

# =========================
# Ejecuta scraping para todas las fuentes guardadas en MongoDB
# =========================
def scraping_todas_las_fuentes():
    fuentes = list(coleccion_fuentes.find())
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
        print(f"\n[{hora_inicio}] 🔁 Lanzando scraping de todas las fuentes...")
        
        # Ejecutar scraping de todas las fuentes
        scraping_todas_las_fuentes()
        
        # Variar el intervalo aleatoriamente entre -20% y +20%
        factor = random.uniform(0.8, 1.2)
        espera_min = SCRAPING_FREQ_MIN * factor
        espera_seg = espera_min * 60

        hora_siguiente = datetime.now() + timedelta(seconds=espera_seg)

        print(f"🕒 Esperando {espera_min:.2f} minutos para la siguiente ejecución...")
        print(f"🕒 Próxima ejecución a las {hora_siguiente.strftime('%H:%M:%S')}")

        # Pausar hasta la próxima ejecución
        time.sleep(espera_seg)

# =========================
# Lanza el scheduler en un hilo en segundo plano al iniciar la app
# =========================
def iniciar_scheduler_en_segundo_plano():
    hilo = threading.Thread(target=scheduler_loop, daemon=True)
    hilo.start()
