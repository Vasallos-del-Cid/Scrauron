import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  GridComponent,
  GridModule,
  PageService,
  ToolbarService,
  SortService,
  FilterService,
  EditService,
} from '@syncfusion/ej2-angular-grids';
import { DialogComponent, DialogModule } from '@syncfusion/ej2-angular-popups';
import { SwitchModule } from '@syncfusion/ej2-angular-buttons';
import { FormCrearFuentesComponent } from './form-crear-fuentes/form-crear-fuentes.component';
import { FuenteService } from './fuentes.service';
import { Fuente } from './fuente.model';
import { CrudAbstractMethodsComponent } from '../../core/services/data-service/crud-abstract-methods.component';

@Component({
  selector: 'app-fuentes',
  standalone: true,
  imports: [
    CommonModule,
    GridModule,
    SwitchModule,
    DialogModule,
    FormCrearFuentesComponent,
  ],
  providers: [
    PageService,
    ToolbarService,
    SortService,
    FilterService,
    EditService,
  ],
  templateUrl: './fuentes.component.html',
  styleUrls: ['./fuentes.component.css'],
})

/**
 * Componente para manejar la lógica de negocio de las fuentes
 *
 * usa CrudAbstractMethodsComponent para manejar la lógica CRUD, teniendo disponibles sus métodos
 *
 * necesita implementar
 * - el método getSeleccionado() para obtener el item seleccionado
 * - el método servicio para definir el servicio a usar
 *
 * usa el formulario FormCrearFuentesComponent para crear y editar fuentes
 *
 * @see {@link FormCrearFuentesComponent} para más información sobre el formulario
 *
 * para el acceso a datos:
 * @see {@link CrudAbstractMethodsComponent} para más información sobre la lógica CRUD
 * @see {@link FuenteService} para más información sobre el servicio de fuentes
 * @See {@link DataService} para más información sobre las llamadas http a la API
 */
export class FuentesComponent
  extends CrudAbstractMethodsComponent<Fuente>
  implements OnInit
{
  @ViewChild('grid') public grid?: GridComponent;
  @ViewChild('dialogoFuente') public formularioFuente?: DialogComponent;
  @ViewChild('formularioFuente')
  public formularioFuenteComponent?: FormCrearFuentesComponent;

  getSeleccionado(): Fuente {
    return (this.itemSeleccionado as Fuente) ?? [];
  }
  override servicio: FuenteService;

  public toolbar: any[] = [
    { text: 'Crear', id: 'Crear', prefixIcon: 'e-add' },
    { text: 'Editar', id: 'Editar', prefixIcon: 'e-edit' },
    { text: 'Eliminar', id: 'Eliminar', prefixIcon: 'e-delete' },
    {
      text: 'Limpiar Filtros',
      id: 'Reset',
      prefixIcon: 'e-filter-clear',
      align: 'Right',
      disabled: true,
    },
    'Search',
  ];

  public pageSettings = { pageSizes: true, pageSize: 10 };
  public editSettings = {
    allowEditing: false,
    allowDeleting: false,
    allowAdding: false,
  };
  dialogTitle = 'Formulario'; // Título del modal a mostrar

  /**
   * permite el acceso a los métodos y propiedades del servicio de fuentes
   * @param fuenteService los metodos base para CRUD se definen en CrudService que es implementado por el servicio, no es necesario definirlos aquí, solo se deben sobreescribir para definir callbacks o success/failure específicos
   */
  constructor(private fuenteService: FuenteService) {
    super();
    this.servicio = fuenteService;
  }

  ngOnInit(): void {
    // Inicializa el componente y carga el grid
    this.cargarDatos(); //método heredado de CrudComponent
  }

  toolbarClick(args: any): void {
    switch (args.item.id) {
      case 'Crear':
        this.abrirDialogoCrear();
        break;
      case 'Editar':
        this.abrirDialogoEditar();
        break;
      case 'Eliminar':
        let id = (this.grid?.getSelectedRecords()[0] as Fuente)._id || '';
        this.fuenteService.delete(id, {
          callback: () => {
            this.grid?.clearSelection();
          },
        });
        break;
      case 'Reset':
        this.grid?.clearFiltering();
        this.grid?.search('');
        this.desactivarResetFiltros();
        break;
    }
  }

  abrirDialogoCrear(): void {
    this.modoEdicion = false;
    this.itemSeleccionado = null;
    this.dialogTitle = 'Crear Nueva Fuente';
    this.formularioFuente?.show();
  }

  abrirDialogoEditar(): void {
    const seleccionados = this.grid?.getSelectedRecords();
    if (seleccionados && seleccionados.length > 0) {
      this.modoEdicion = true;
      this.itemSeleccionado = { ...seleccionados[0] } as Fuente;
      this.dialogTitle = 'Editar Fuente';
      this.formularioFuente?.show();
    }
  }

  cancelarFuente(): void {
    this.formularioFuente?.hide();
    this.itemSeleccionado = null;
    this.modoEdicion = false;
  }

  onActionBegin(args: any): void {
    if (args.requestType === 'filtering' || args.requestType === 'searching') {
      console.log('➡️ Se ha aplicado un filtro o una búsqueda');
    }
  }

  onActionComplete(args: any): void {
    if (args.requestType === 'filtering' || args.requestType === 'searching') {
      const filtrosActivos =
        (this.grid?.filterSettings?.columns?.length ?? 0) > 0 ||
        (this.grid?.searchSettings?.key?.length ?? 0) > 0;
      console.log('➡️ ⚠️ ¿Filtros activos?', filtrosActivos);
      this.activarODesactivarResetFiltros(filtrosActivos);
    }
  }

  dataBound(): void {
    const filtrosActivos =
      (this.grid?.filterSettings?.columns?.length ?? 0) > 0 ||
      (this.grid?.searchSettings?.key?.length ?? 0) > 0;
    this.activarODesactivarResetFiltros(filtrosActivos);
  }

  activarODesactivarResetFiltros(activo: boolean): void {
    const resetButton = this.grid?.toolbarModule?.toolbar?.items.find(
      (item: any) => item.id?.endsWith('Reset')
    );
    if (resetButton) {
      resetButton.disabled = !activo;
      this.grid?.toolbarModule?.toolbar?.refreshOverflow();
    }
  }

  desactivarResetFiltros(): void {
    this.activarODesactivarResetFiltros(false);
  }

  /**
   * permite definir las acciones a realizar despues de guardar una fuente
   * la logica de guardar se define en el servicio
   * @param fuente
   */
  override guardar(fuente: Fuente): void {
    super.guardar(fuente);
    this.formularioFuenteComponent?.cancelarForm();
    this.formularioFuente?.hide();
  }

  switchChange(args: any, rowData: any): void {
    const activa = args.checked;
    const id = rowData._id;
    if (!id) return;
    super.actualizar(id, { activa: activa }, { success: () => {} }); //en el succes no se hace nada
  }
}
