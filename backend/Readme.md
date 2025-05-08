# Backend

Python con flask y MongoDB

## Requisitos

- Python 3.8 o superior
- pip
- MongoDB 4.0 o superior
  - ``pip install pymongo``
- [MongoDB CLOUD](https://cloud.mongodb.com) en nube (para produccion)
  - para poder acceder se debe dar acceso a la IP donde arranque la aplicaccion:
    - Ir al proyecto --> Security --> Network Access --> Add IP Address --> Access List Entry: X.X.X.X [https://www.showmyip.com/](https://www.showmyip.com/)
- [MongoDB Community Server](https://www.mongodb.com/try/download/community) local (para desarrollo en local)
  - comprobar el puerto de MongoDB (27017 por defecto) y asegurarse de que el servicio esté en ejecución. ``mongod --version``. Usar ``mongosh`` para el acceso a la shell de MongoDB.
- dotenv
  - ``pip install dotenv``
- archivo .env con las variables de entorno necesarias para la conexión a la base de datos y el puerto del servidor.
- Instalar las herramientas de desarrollo de C++ (necesario para dependencia de Scrapy - twisted-iocpsupport)
  - Debes instalar el compilador de C++ necesario para compilar extensiones de Python:
    - Descarga e instala Microsoft C++ Build Tools.
    - [Descargar MsBuildTools](https://visualstudio.microsoft.com/es/visual-cpp-build-tools/)
    - Durante la instalación, selecciona el componente "Desarrollo para escritorio con C++".
    - Asegúrate de incluir las herramientas de compilación y los encabezados necesarios.
- Postman (opcional)

## Instalación

```bash
cd ./backend 
## python -m venv venv # esto es opcional, pero se recomienda crear un entorno virtual sengun copilot

# python -m pip install --upgrade pip # (opcional) si da lgun fallo al instalar --> actualizar pip a la última versión
pip install -r requirements.txt
```

## Ejecución

```bash
python run.py

# para entorno de desarrollo local
python run.py --env local
```

Esto iniciará el servidor en modo de desarrollo y estará disponible en http://127.0.0.1:5000/api por defecto.

### Ejecucion en Intellij (Pycharm) 

Abrir la carpeta backend 

incluir una run configuration

- Entorno de python
- script --> `C:/[raizDelProyecto]/backend/run.py`
- working directory: `C:/[raizDelProyecto]/backend/`
- Environment Variables: `FLASK_ENV=development;PYTHONUNBUFFERED=1;FLASK_RELOAD=false`
- path ton .env files: `C:/[raizDelProyecto]/backend/.env`
