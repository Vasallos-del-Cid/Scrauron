import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GridComponent, GridModule, PageService, ToolbarService, SortService, FilterService, EditService } from '@syncfusion/ej2-angular-grids';

@Component({
  selector: 'app-intereses',
  standalone: true,
  imports: [CommonModule, GridModule],
  providers: [PageService, ToolbarService, SortService, FilterService, EditService],
  templateUrl: './intereses.component.html',
  styleUrls: ['./intereses.component.css']
})
export class InteresesComponent implements OnInit {

  @ViewChild('grid') public grid?: GridComponent;

  public intereses: any[] = [];

  public toolbar: any[] = [
    'Add', 'Edit', 'Delete', 'Update', 'Cancel', 'Search',
  ];

  public pageSettings = { pageSizes: true, pageSize: 10 };
  public editSettings = { allowEditing: true, allowDeleting: true, allowAdding: true };

  constructor() {}

  ngOnInit(): void {
    this.cargarInteresesMock();
  }

  cargarInteresesMock(): void {
    this.intereses = [
      {
        nombre: "Wilkinson",
        num_menciones: 150,
        usuario_creador: "rodrigo.diaz",
        num_usuarios: 5,
        fecha_creacion: "2025-04-20",
        estado: "Activo"
      },
      {
        nombre: "Crisis Arancelaria",
        num_menciones: 240,
        usuario_creador: "ana.lopez",
        num_usuarios: 8,
        fecha_creacion: "2025-03-15",
        estado: "Activo"
      },
      {
        nombre: "Competencia XYZ",
        num_menciones: 80,
        usuario_creador: "rodrigo.diaz",
        num_usuarios: 2,
        fecha_creacion: "2025-02-10",
        estado: "Inactivo"
      }
    ];
  }

  toolbarClick(args: any): void {
    if (args.item.id === 'Reset') {
      this.grid?.clearFiltering();
      this.grid?.search('');
    }
  }

  dataBound(): void {
    const filtered = (this.grid?.filterSettings?.columns?.length ?? 0) > 0 ||
                     (this.grid?.searchSettings?.key?.length ?? 0) > 0;
    this.activarODesactivarResetFiltros(filtered);
  }

  activarODesactivarResetFiltros(activo: boolean): void {
    const resetButton = this.grid?.toolbarModule?.toolbar?.items.find((item: any) => item.id === this.grid?.element.id + '_Reset');
    if (resetButton) {
      resetButton.disabled = !activo;
    }
  }
}
