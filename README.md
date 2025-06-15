# Scrauron


## Frontend

### Crear el proyecto

La version de creacion del proyecto --> angular@19.2.8

```bash
npm install -g @angular/cli
```

```bash
ng new frontend

# estio --> CSS
# prerenderind --> N
```

Instalacion del proyecto y dependencias

```bash
cd .\frontend

npm install
```

### Run project

```
ng serve -o
```

Se mostrará el proyecto en `http://localhost:4200/`

### Incusion de la libreria Syncfusion

Se puede incluir cualquier componente con:

```bash
npm install @syncfusion/ej2-angular-grids --save
```

#### Instalacion y licenciamiento de Syncfusion

1. Instalar Syncfusion y registrarse --> [ver documentacion](https://ej2.syncfusion.com/angular/documentation/installation-and-upgrade/installation-using-web-installer "https://ej2.syncfusion.com/angular/documentation/installation-and-upgrade/installation-using-web-installer")
2. Es necesario licenciar la libreria de Syncfusion  (Enterprise Edition - Community license)--> [ver documentacion](https://ej2.syncfusion.com/angular/documentation/licensing/overview "https://ej2.syncfusion.com/angular/documentation/licensing/overview")

   1. Para que la licencia no este en el codigo hacer lo siguiente

      ```
      #powershell

      # instalar dotenv para que pueda generar el fichero
      npm install dotenv --save-dev

      # almacenar la clave en variable de la terminal 
      $Env:SYNCFUSION_LICENSE="XXX_tu_clave_generada_en_el_paso_anteror_XXX"

      # ejecutar
      npm run generarLicencia
      ```

      Existe un script en ~frontend/scripts que guarda la variable en un fichero de environment que no se incluye en git

      Este script se lanza tras ejecutar npm run generarLicencia (ver scripts del package.json --> generarLicencia).

      Si el archivo ya estaba creado, no hace nada
3. Incluir la licencia en el proyecto

   1. En el main.ts incluir este bloque

      ```
      //Para la inclusion de synfusion en el main.ts
      import { registerLicense } from '@syncfusion/ej2-base';
      import { syncfusionLicense } from './environments/syncfusion-license';

      registerLicense(syncfusionLicense);
      ```

## Inclusion de componentes de syncfusion

instalar la dependencia

```bash
ng add @syncfusion/ej2-angular-grids
```

Con el comando, se deben haber incluido las dependencias necesarias para el componente en:

- Styles.css (import de la dependencia de node modules)
  - Styles del angular.json (idem)
- app-coomponent (componente declarado en el imports)

Con eso ya estaria el componente listo para usarse

## Backend

### Instalar dependencias

```
cd ./backend 
## python -m venv venv # esto es opcional, pero se recomienda crear un entorno virtual

# python -m pip install --upgrade pip # (opcional) si da lgun fallo al instalar --> actualizar pip a la última versión
pip install -r requirements.txt
```

### Run project

```
python run.py
```

### OPENAI TOKEN

para conseguir un token de openAi, ir a https://platform.openai.com/settings/organization/api-keys y crear nuevo Secret Key

* Incluir en `.env` del backend

### Copiar la BBDD de mongo desde CLOUD a local

- ejecutar
  - copiar a local
    - `mongodump --uri="mongodb+srv://user:pass@scrauroncluster.pwatkak.mongodb.net/baseDatos" --out=dump_atlas`
  - Restaurar en mongo local (sobreescribe la bbdd local)
    - `mongorestore --drop dump_atlas`
