import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CrudGenericComponent } from '../../core/plantillas/crud-generic/crud-generic.component';
import { ConceptosService } from './conceptos.service';
import { Conceptos } from './Conceptos.model';
import { ColumnConfig } from '../../core/plantillas/crud-generic/column.model';
import { FormFieldConfig } from '../../core/plantillas/crud-generic/form-field.model';
import { Validators } from '@angular/forms';
import { DataService } from '../../core/services/data-service/data-service.service';

@Component({
  selector: 'app-conceptos',
  standalone: true,
  imports: [CommonModule, CrudGenericComponent],
  templateUrl: './conceptos.component.html',
  styleUrls: ['./conceptos.component.css'],
})
export class ConceptosComponent {
  itemDefault: Partial<Conceptos> = {};
  conceptosService: ConceptosService;
  constructor(public servicio: ConceptosService) {
    this.conceptosService = servicio;
  }
  columns: ColumnConfig[] = [
    { field: 'nombre', headerText: 'Nombre', isPrimaryKey: true, width: 250 },
    { field: 'descripcion', headerText: 'Descripción' },
    /* { field: 'keywords', headerText: 'Keywords', width: 150 },
    {
      field: 'publicaciones_relacionadas_ids',
      headerText: 'Nº Pub Rel.',
      width: 120,
      textAlign: 'Center',
    },

      TODO: estos campos se deben agregar en back
    { field: 'activa', headerText: 'Activa', type: 'boolean', width: 80, textAlign: 'Center' },
    { field: 'num_menciones', headerText: 'Menciones', textAlign: 'Right' },
    { field: 'usuario_creador', headerText: 'Creador' },
    { field: 'num_usuarios', headerText: 'Usuarios', textAlign: 'Right' },
    { field: 'fecha_creacion', headerText: 'Fecha Creación', type:'datetime', format:'yyyy-MM-dd' } */
  ];

  formFields: FormFieldConfig[] = [
    {
      name: 'nombre',
      label: 'Nombre',
      type: 'text',
      placeholder: '',
      validators: [Validators.required],
    },
    { name: 'descripcion', label: 'Descripción', type: 'text',placeholder: '' },
    {
      name: 'keywords',
      label: 'Keywords',
      type: 'text',
      placeholder: 'sepáralos por comas',
    },
    /* {
      name: 'publicaciones_relacionadas_ids',
      label: 'Publicaciones Relacionadas',
      type: 'select',
      options: [{ value: 'twiter', label: 'Twitter' }], // si quieres cargarlas dinámicamente
    }, */
  ];
}
