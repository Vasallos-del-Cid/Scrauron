import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CrudGenericComponent } from '../../core/plantillas/crud-generic/crud-generic.component';
import { AreasService } from './areas.service';
import { Areas } from './areas.model';
import { ColumnConfig } from '../../core/plantillas/crud-generic/column.model';
import { FormFieldConfig } from '../../core/plantillas/crud-generic/form-field.model';
import { Validators } from '@angular/forms';
import { DataService } from '../../core/services/data-service/data-service.service';

@Component({
  selector: 'app-intereses',
  standalone: true,
  imports: [CommonModule,CrudGenericComponent],
  templateUrl: './areas.component.html',
  styleUrls: ['./areas.component.css']
})
export class AreasComponent {
  itemDefault: Partial<Areas> = {};
areasService: AreasService;
  constructor(public servicio: AreasService) {
    this.areasService = servicio;
   }
  columns: ColumnConfig[] = [
    { field: 'nombre', headerText: 'Nombre', isPrimaryKey: true, width: 150 },
    //{ field: 'descripcion', headerText: 'Descripción', width: 250 },
    { field: 'conceptos_interes_ids', headerText: 'Conceptos', width: 150 },
    { field: 'fuentes_ids', headerText: 'Fuentes', width: 120, textAlign: 'Center' },
    // Tus campos estáticos adicionales…
    { field: 'num_menciones', headerText: 'Menciones', textAlign: 'Right' },
    { field: 'usuario_creador', headerText: 'Creador' },
    { field: 'fecha_creacion', headerText: 'Fecha Creación', type:'datetime', format:'yyyy-MM-dd' },
    { field: 'activa', headerText: 'Activa', type: 'boolean', width: 80, textAlign: 'Center' }
  ];

  formFields: FormFieldConfig[] = [
    { name: 'nombre', label: 'Nombre', type: 'text', validators: [ Validators.required ] },
    { name: 'conceptos_interes_ids', label: 'Conceptos', type: 'text', placeholder: 'sepáralas por comas' },
    {
      name: 'fuentes_ids',
      label: 'Fuentes',
      type: 'select',
      options: [{ value: 'twiter', label: 'Twitter'}, ]  // si quieres cargarlas dinámicamente
    }
  ];
 
}
