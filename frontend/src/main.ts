import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { L10n, setCulture } from '@syncfusion/ej2-base';
import { registerLicense } from '@syncfusion/ej2-base';
import { syncfusionLicense } from './environments/syncfusion-license';

registerLicense(syncfusionLicense);

// Cargar idioma global
L10n.load({
  'es-ES': {
    grid: {
      EmptyRecord: 'No hay datos disponibles',
      GroupDropArea: 'Arrastra un encabezado de columna aquí para agrupar',
      UnGroup: 'Haz clic aquí para desagrupar',
      EmptyDataSourceError: 'Datasource no debe estar vacío en la carga inicial',
      Add: 'Crear',
      Edit: 'Editar',
      Cancel: 'Cancelar',
      Update: 'Actualizar',
      Delete: 'Eliminar',
      Print: 'Imprimir',
      Pdfexport: 'Exportar PDF',
      Excelexport: 'Exportar Excel',
      Wordexport: 'Exportar Word',
      Search: 'Buscar...',
      Save: 'Guardar',
    },
    pager: {
      currentPageInfo: '{0} de {1} páginas',
      totalItemsInfo: '({0} registros)',
      firstPageTooltip: 'Ir a la primera página',
      lastPageTooltip: 'Ir a la última página',
      nextPageTooltip: 'Ir a la página siguiente',
      previousPageTooltip: 'Ir a la página anterior',
      nextPagerTooltip: 'Ir al siguiente paginador',
      previousPagerTooltip: 'Ir al paginador anterior'
    }
  }
});

// Establecer cultura general (esto pone formato de fechas y números también)
setCulture('es-ES');

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
