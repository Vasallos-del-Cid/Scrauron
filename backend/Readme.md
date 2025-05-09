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

## Creacion de un entorno virtual
un entorno virtual es una herramienta que ayuda a mantener las dependencias requeridas por diferentes proyectos en espacios separados. Si no se crea un entorno virtual, todas las dependencias se instalarán en el sistema globalmente.
- [Documentación de Python](https://docs.python.org/es/3/tutorial/venv.html)
- Crear un entorno virtual:
  
  - ```bash
    python -m venv venv
    
    # Para crearlo con una versión específica de Python(debe estar instalada):
    py -3.10 -m venv venv
    # comprobar versiones de python instaladas
    py -0
    ```
- Activar el entorno virtual __SE DEBE HACER SIEMPRE ANTES DE INCIAR LA APLICACION__:
  - En Windows:
    ```bash
    venv\Scripts\activate
    ```
  - En Linux o macOS:
    ```bash
    source venv/bin/activate
    ```
  - En la consola de Linux o macOS, el prompt cambiará para indicar que el entorno virtual está activo. Por ejemplo, puede verse algo como esto:
    ```bash
    (venv) PS C:/path/to/project>
    
    # comprobar la versión de python
    python --version
    # Comprobar librerías instaladas en el entorno virtual
    pip list
    ```
- Desactivar el entorno virtual __CUANDO SE TERMINA DE USAR__:
  - ```bash
    deactivate
    ```
- Instalar las dependencias necesarias:
  - ```bash
    pip install -r requirements.txt
    ```
- Si se desea instalar una dependencia adicional, se puede hacer con el siguiente comando:
  - ```bash
    pip install nombre_dependencia
    ```
- Para guardar las dependencias instaladas en un archivo `requirements.txt`, se puede usar el siguiente comando:
  - ```bash
    pip freeze > requirements.txt
    ```


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

Incluir el entorno virtual en el proyecto:
- File --> Settings --> Project: [nombre del proyecto] --> Python Interpreter
- añadir el entorno virtual creado en la carpeta del proyecto (venv) --> `C:/[raizDelProyecto]/backend/venv/Scripts/python.exe`
- si no aparece el entorno virtual, añadirlo manualmente:
  - File --> Settings --> Project: [nombre del proyecto] --> Python Interpreter
  - click en la rueda dentada --> Add... --> Existing environment
  - seleccionar el entorno virtual creado en la carpeta del proyecto (venv) --> `C:/[raizDelProyecto]/backend/venv/Scripts/python.exe`
  - click en OK

Incluir una run configuration

- Entorno de python
- script --> `C:/[raizDelProyecto]/backend/run.py`
- working directory: `C:/[raizDelProyecto]/backend/`
- Interpreter: `C:/[raizDelProyecto]/backend/venv/Scripts/python.exe`
- Environment Variables:
  - Para usar hot reload, se puede usar estas variables y el siguiente comando:
    - No permite debugging
    - `FLASK_ENV=development;PYTHONUNBUFFERED=1;FLASK_RELOAD=true`
    - Lanzar con __RUN__
  - Para hacer debugging, se puede usar el siguiente comando:
    - No permite hot reload
    - `FLASK_ENV=development;PYTHONUNBUFFERED=1;FLASK_RELOAD=false`
    - Lanzar con __DEBUG__
- Script parameters: `--env local`
- path ton .env files: `C:/[raizDelProyecto]/backend/.env`
