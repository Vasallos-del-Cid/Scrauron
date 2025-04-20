# Rodrigo

Rodrigo Diaz de Vivar, el Cid Campeador

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

      # ejecutar uno de los dos
      npm install
      npm run prebuild
      ```

      Existe un script en ~frontend/scripts que guarda la variable en un fichero de environment que no se incluye en git

      Este script se lanza tras ejecutar npm install o npm run prebuild (ver scripts del package.json --> postinstall)
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
