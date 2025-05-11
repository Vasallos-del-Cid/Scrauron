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
import { CrudComponent } from '../../core/services/api-service/crud-abstract.component';

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
export class FuentesComponent extends CrudComponent<Fuente> implements OnInit {
  @ViewChild('grid') public grid?: GridComponent;
  @ViewChild('dialogoFuente') public dialogoFuente?: DialogComponent;

  /**
   * Referencia al componente FormCrearFuentesComponent
   * para poder acceder a sus métodos y propiedades
   */
  public fuenteSeleccionada: Fuente | null = null;
  /**
   * Indica si el formulario está en modo edición o no.
   */
  override modoEdicion = false;

  /**
   * desde CrudComponent (abstract) que implementa CrudService y define el servicio
   * debe estar definido, se asigna en el constructor
   */
  override servicio;

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
        this.borrar(this.grid?.getSelectedRecords()[0] as Fuente, {
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
    this.fuenteSeleccionada = null;
    this.dialogTitle = 'Crear Nueva Fuente';
    this.dialogoFuente?.show();
  }

  abrirDialogoEditar(): void {
    const seleccionados = this.grid?.getSelectedRecords();
    if (seleccionados && seleccionados.length > 0) {
      this.modoEdicion = true;
      this.fuenteSeleccionada = { ...seleccionados[0] } as Fuente;
      this.dialogTitle = 'Editar Fuente';
      this.dialogoFuente?.show();
    }
  }

  cancelarFuente(): void {
    this.dialogoFuente?.hide();
    this.fuenteSeleccionada = null;
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
   * permite definir las acciones a realizar al guardar una fuente
   * la logica de guardar se define en el servicio
   * @param fuente 
   */
  override guardar(fuente: Fuente): void {
    super.guardar(fuente, {
      callback: () => {
        this.dialogoFuente?.hide();
        this.fuenteSeleccionada;
        console.log('✔️ Guardado finalizado');
      },
    });
  }

  switchChange(args: any, rowData: any): void {
    const activa = args.checked;
    const id = rowData._id;
    if (!id) return;
    this.fuenteService.update(id, { activa: activa });
  }
}
