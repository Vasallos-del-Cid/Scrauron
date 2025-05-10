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
export class FuentesComponent implements OnInit {
  @ViewChild('grid') public grid?: GridComponent;
  @ViewChild('dialogoFuente') public dialogoFuente?: DialogComponent;

  public fuentes: Fuente[] = [];

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
  public modoEdicion = false;
  public fuenteSeleccionada: Fuente | null = null;

  constructor(private fuenteService: FuenteService) {}

  ngOnInit(): void {
    this.cargarFuentes();
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
        this.borrarFuente();
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
    this.dialogoFuente?.show();
  }

  abrirDialogoEditar(): void {
    const seleccionados = this.grid?.getSelectedRecords();
    if (seleccionados && seleccionados.length > 0) {
      this.modoEdicion = true;
      this.fuenteSeleccionada = { ...seleccionados[0] } as Fuente;
      this.dialogoFuente?.show();
    }
  }

  cancelarFuente(): void {
    this.dialogoFuente?.hide();
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

  cargarFuentes(): void {
    this.fuenteService.getFuentes((data) => {
      this.fuentes = data;
    });
  }

  borrarFuente(): void {
    const seleccionados = this.grid?.getSelectedRecords();
    if (seleccionados && seleccionados.length > 0) {
      const fuente = seleccionados[0] as Fuente;
      if (fuente._id) {
        this.fuenteService.deleteFuente(fuente._id, () => {
          this.cargarFuentes();
          console.log(`Fuente ${fuente.nombre} eliminada`);
        });
      }
    }
  }

  guardarFuente(fuente: Fuente): void {
    if (this.modoEdicion && this.fuenteSeleccionada?._id) {
      this.fuenteService.updateFuente(this.fuenteSeleccionada._id, fuente, {
        success: () => {
          this.cargarFuentes();
          this.dialogoFuente?.hide();
        },
      });
    } else {
      this.fuenteService.createFuente(fuente, {
        success: () => {
          this.cargarFuentes();
          this.dialogoFuente?.hide();
        },
      });
    }
  }

  switchChange(args: any, rowData: any): void {
    const activa = args.checked;
    const id = rowData._id;
    if (!id) return;
    this.fuenteService.updateFuente(
      id,
      { activa: activa },
      {
        success: () => console.log(`Fuente ${rowData.nombre} actualizada`),
        failure: (err) => console.error('Error al actualizar fuente:', err),
      }
    );
  }
}
