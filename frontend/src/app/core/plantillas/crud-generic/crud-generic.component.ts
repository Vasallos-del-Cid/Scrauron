import { Component, Input, OnInit, ViewChild } from '@angular/core';
import {
  GridComponent,
  GridModule,
  PageService,
  SortService,
  FilterService,
  ToolbarService,
  QueryCellInfoEventArgs,
  ToolbarItems,
} from '@syncfusion/ej2-angular-grids';
import { Tooltip } from '@syncfusion/ej2-popups';
import { Switch } from '@syncfusion/ej2-buttons';
import { DialogModule } from '@syncfusion/ej2-angular-popups';
import { SwitchModule } from '@syncfusion/ej2-angular-buttons';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';

import { ColumnConfig } from './column.model';
import { FormFieldConfig } from './form-field.model';
import { DataService } from '../../services/data-service/data-service.service';

@Component({
  selector: 'app-crud-generic',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    GridModule,
    DialogModule,
    SwitchModule,
  ],
  providers: [PageService, SortService, FilterService, ToolbarService],
  templateUrl: './crud-generic.component.html',
  styleUrls: ['./crud-generic.component.css'],
})
export class CrudGenericComponent implements OnInit {
  @Input() columns: ColumnConfig[] = [];
  @Input() formFields: FormFieldConfig[] = [];
  @Input() servicio!: DataService<any>;
    @Input() toolbarItems: any[] = [
    { text: 'Crear', id: 'Crear', prefixIcon: 'e-add' },
    { text: 'Editar', id: 'Editar', prefixIcon: 'e-edit' },
    { text: 'Eliminar', id: 'Eliminar', prefixIcon: 'e-delete' },
    { text: 'Limpiar Filtros', id: 'Reset', prefixIcon: 'e-clear-filter', align: 'Right', disabled: true },
    'Search'
  ];
  @Input() dialogTitle = 'Formulario';
  @Input() itemDefault: Record<string, any> = {};

  @ViewChild('grid', { static: true }) grid!: GridComponent;
  @ViewChild('dialog', { static: true }) dialog!: any;

  form!: FormGroup;
  modoEdicion = false;

  constructor(private fb: FormBuilder) {}

  ngOnInit(): void {
    this.servicio.getAll();
    const group: any = {};
    this.formFields.forEach((f) => {
      group[f.name] = [this.itemDefault[f.name] ?? '', f.validators || []];
    });
    this.form = this.fb.group(group);
  }

  // Este handler se invoca para cada celda al renderizarse
  queryCellInfo(args: QueryCellInfoEventArgs) {
    const field = args?.column?.field as string;
    const config = (this.columns as ColumnConfig[]).find(
      (c) => c.field === field
    );
    if (!config) {
      return;
    }
    const data = args.data as any;

    const cell = args.cell as HTMLElement;
    const value = data[field];

    // 1) Si es string (si no se define se asume string) y el valor es array
    if ((config.type === 'string' || !config.type) && Array.isArray(value)) {
      const arr = value as any[];
      if (arr.length) {
        // texto: primer elemento + “… más” si corresponde
        const moreCount = arr.length - 1;
        cell.innerText = moreCount > 0 ? `${arr[0]} … más` : `${arr[0]}`;

        // tooltip HTML con <br> y enableHtml
        new Tooltip(
          {
            content: arr.join('<br/>'),
            opensOn: 'Hover',
          },
          cell
        );
      }
    }
    // 2) Si es boolean → Switch EJ2
    else if (config.type === 'boolean' || typeof value === 'boolean') {
      cell.innerHTML = '';
      const chk = document.createElement('input');
      chk.type = 'checkbox';
      chk.checked = !!value;
      // Actualiza la entidad al cambiar
      chk.addEventListener('change', () => {
        const updated = { ...data, [field]: chk.checked };
        this.servicio.update(data._id, updated, {
          success: () => this.grid.refresh(),
        });
      });
      // Anexamos al <td>
      cell.appendChild(chk);
      return;
    }
  }

  toolbarClick(args: any) {
    switch (args.item.id) {
      case 'Crear':
        this.modoEdicion = false;
        this.form.reset(this.itemDefault);
        this.dialog.show();
        break;
      case 'Editar':
        const sel = (this.grid.getSelectedRecords()[0] as any);
        if (sel) {
          this.modoEdicion = true;
          this.form.patchValue(sel);
          this.dialog.show();
        }
        break;
      case 'Eliminar':
        const rec = (this.grid.getSelectedRecords()[0] as any);
        if (rec && rec._id) {
          this.servicio.delete(rec._id, { success: () => this.grid.clearSelection() });
        }
        break;
      case 'Reset':
        this.grid.clearFiltering();
        this.grid.search('');
        break;
    }
  }

  // Guardar/actualizar
  submit() {
    if (!this.form.valid) { return; }
    const value = this.form.value;
    if (this.modoEdicion && (value as any)._id) {
      this.servicio.update((value as any)._id, value, { success: () => this.dialog.hide() });
    } else {
      this.servicio.create(value, { success: () => this.dialog.hide() });
    }
    this.form.reset(this.itemDefault);
  }

  // Cerrar dialog
  cancel() {
    this.form.reset(this.itemDefault);
    this.dialog.hide();
  }
}
