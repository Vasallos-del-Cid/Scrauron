import subprocess

SCRAPING_FREQ = 60

def ejecutar_scraping(url):
    return subprocess.run(["python", "app/spiders/spider_executor.py", url], check=True)

   
