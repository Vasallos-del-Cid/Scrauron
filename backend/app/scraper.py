import subprocess

# Ejecuta el script spider_executor.py como un subproceso externo de Python, pasando la url como argumento.
# Se lanza un subproceso para ejecutar el job de scraping sin bloquear el hilo principal.
def ejecutar_scraping(url):
    print("Ejecutando subproceso de scraping...")
    return subprocess.run(["python", "app/spiders/spider_executor.py", url], check=True)

   
