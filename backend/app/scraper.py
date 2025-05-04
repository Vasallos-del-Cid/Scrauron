import subprocess

def ejecutar_scraping(url):
    subprocess.run(["python", "app/spiders/spider_executor.py", url], check=True)

   
