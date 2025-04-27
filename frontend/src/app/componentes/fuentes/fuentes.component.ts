import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GridComponent, GridModule, PageService, ToolbarService, SortService, FilterService, EditService } from '@syncfusion/ej2-angular-grids';
import { DialogComponent, DialogModule } from '@syncfusion/ej2-angular-popups';
import { SwitchModule } from '@syncfusion/ej2-angular-buttons';
import { FormCrearFuentesComponent } from './form-crear-fuentes/form-crear-fuentes.component';

@Component({
  selector: 'app-fuentes',
  standalone: true,
  imports: [CommonModule, GridModule, SwitchModule, DialogModule, FormCrearFuentesComponent],
  providers: [PageService, ToolbarService, SortService, FilterService, EditService],
  templateUrl: './fuentes.component.html',
  styleUrls: ['./fuentes.component.css']
})
export class FuentesComponent implements OnInit {

  @ViewChild('grid') public grid?: GridComponent;
  @ViewChild('dialogoFuente') public dialogoFuente?: DialogComponent;

  public fuentes: any[] = [];

  public toolbar: any[] = [
    { text: 'Crear', id: 'Crear', prefixIcon: 'e-add' },
    { text: 'Editar', id: 'Editar', prefixIcon: 'e-edit' },
    { text: 'Eliminar', id: 'Eliminar', prefixIcon: 'e-delete' },
    'Search',
    { text: 'Limpiar Filtros', id: 'Reset', prefixIcon: 'e-clear-icon', align: 'Right', disabled: true }
  ];

  public pageSettings = { pageSizes: true, pageSize: 10 };
  public editSettings = { allowEditing: false, allowDeleting: false, allowAdding: false };
  public modoEdicion = false;
  public fuenteSeleccionada: any = null;

  constructor() {}

  ngOnInit(): void {
    this.cargarFuentesMock();
  }

  cargarFuentesMock(): void {
    this.fuentes = [
      {
        nombre: "Twitter",
        tipo: "Red Social",
        activo: true,
        fecha_alta: "2024-04-01"
      },
      {
        nombre: "La Vanguardia",
        tipo: "Prensa Escrita",
        activo: true,
        fecha_alta: "2024-04-15"
      },
      {
        nombre: "Canal Noticias Telegram",
        tipo: "Canal Telegram",
        activo: false,
        fecha_alta: "2024-03-20"
      }
    ];
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
        this.eliminarFuente();
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
      this.fuenteSeleccionada = { ...seleccionados[0] };
      this.dialogoFuente?.show();
    }
  }

  eliminarFuente(): void {
    const seleccionados = this.grid?.getSelectedRecords();
    if (seleccionados && seleccionados.length > 0) {
      const nombre = (seleccionados[0] as { nombre: string })['nombre'];
      this.fuentes = this.fuentes.filter(f => f.nombre !== nombre);
      this.grid?.refresh();
      console.log(`Fuente ${nombre} eliminada`);
    }
  }

  guardarFuente(fuente: any): void {
    if (this.modoEdicion) {
      const index = this.fuentes.findIndex(f => f.nombre === this.fuenteSeleccionada.nombre);
      if (index !== -1) {
        this.fuentes[index] = fuente;
      }
    } else {
      this.fuentes.push(fuente);
    }
    this.grid?.refresh();
    this.dialogoFuente?.hide();
  }

  cancelarFuente(): void {
    this.dialogoFuente?.hide();
  }

  dataBound(): void {
    const filtrosActivos = (this.grid?.filterSettings?.columns?.length ?? 0) > 0 ||
                            (this.grid?.searchSettings?.key?.length ?? 0) > 0;
    this.activarODesactivarResetFiltros(filtrosActivos);
  }

  activarODesactivarResetFiltros(activo: boolean): void {
    const resetButton = this.grid?.toolbarModule?.toolbar?.items.find((item: any) => item.id?.endsWith('_Reset'));
    if (resetButton) {
      resetButton.disabled = !activo;
      this.grid?.toolbarModule?.toolbar?.refreshOverflow();
    }
  }

  desactivarResetFiltros(): void {
    this.activarODesactivarResetFiltros(false);
  }

  switchChange(args: any, rowData: any): void {
    rowData.activo = args.checked;
  }
}
