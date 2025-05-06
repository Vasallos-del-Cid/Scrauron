# Backend

Python con flask y MongoDB

## Requisitos
- Python 3.8 o superior
- pip
- MongoDB 4.0 o superior
  - ``pip install pymongo``
- dotenv
  - ``pip install dotenv``
- archivo .env con las variables de entorno necesarias para la conexión a la base de datos y el puerto del servidor.
- Instalar las herramientas de desarrollo de C++ (necesario para dependencia de Scrapy - twisted-iocpsupport)
  - Debes instalar el compilador de C++ necesario para compilar extensiones de Python:

  - Descarga e instala Microsoft C++ Build Tools.
  - Durante la instalación, selecciona el componente "Desarrollo para escritorio con C++".
  - Asegúrate de incluir las herramientas de compilación y los encabezados necesarios.
- virtualenv (opcional)
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
``` 

Esto iniciará el servidor en modo de desarrollo y estará disponible en http://127.0.0.1:5000/api por defecto.
