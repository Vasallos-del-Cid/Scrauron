import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CrudGenericComponent } from '../../core/plantillas/crud-generic/crud-generic.component';
import { ConceptosService } from './conceptos.service';
import { Conceptos } from './Conceptos.model';
import { ColumnConfig } from '../../core/plantillas/crud-generic/column.model';
import { FormFieldConfig } from '../../core/plantillas/crud-generic/form-field.model';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { DataService } from '../../core/services/data-service/data-service.service';
import { finalize } from 'rxjs';
import { AreasService } from '../areas/areas.service';
import { Areas } from '../areas/areas.model';
import { Keyword } from './Keyword.model';

@Component({
  selector: 'app-conceptos',
  standalone: true,
  imports: [
    CommonModule,
    CrudGenericComponent,
    FormsModule,
    ReactiveFormsModule,
  ],
  templateUrl: './conceptos.component.html',
  styleUrls: ['./conceptos.component.css'],
})
export class ConceptosComponent {
  conceptosService: ConceptosService;

  @ViewChild(CrudGenericComponent) crud!: CrudGenericComponent;

  itemDefault = {
    _id: '',
    nombre: '',
    descripcion: '',
    keywords_ids: [],
    areaId: '',
  };

  // wizard state
  step = 1;
  wizardForm: FormGroup;
  keywordsList: Keyword[] = [];
  areas;
  createdId: any;

  constructor(
    public servicio: ConceptosService,
    private fb: FormBuilder,
    private areasService: AreasService
  ) {
    this.conceptosService = servicio;
    this.wizardForm = this.fb.group({
      _id: [''],
      areaId: ['', Validators.required],
      nombre: ['', Validators.required],
      descripcion: [''],
    });

    // Fetch areas from the service
    this.areasService.getAll();

    this.areas = this.areasService.items$;
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
    {
      name: 'descripcion',
      label: 'Descripción',
      type: 'text',
      placeholder: '',
    },
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

  getAreaName(areaId: string): string {
    // If this.areas is an Observable, you need to subscribe to it and store the latest value in a variable.
    // For synchronous access, you need to have a local array (e.g., this.areasList) updated from the Observable.
    // Here is a safe fallback if you want to keep the signature synchronous:
    return ''; // Not possible to synchronously get area name from Observable
  }

  // Paso 1: crear sólo nombre + área
  onCreateName() {
  const { nombre, areaId } = this.wizardForm.value;
  this.conceptosService.createOnlyName(nombre)
    .subscribe(res => {
      // ¡guardamos el id CLARAMENTE!
      this.wizardForm.patchValue({ _id: res._id, areaId });
      this.onGenerateDescription()
      this.step = 2;
    }, err => {
      console.error('Error creando concepto:', err);
    });
}

  // Paso 2: generar descripción
  onGenerateDescription() {
  const id = this.wizardForm.get('_id')!.value;
  if (!id) {
    console.error('No hay ID de concepto para generar descripción');
    return;
  }
  this.conceptosService.generateDescription(id)
    .subscribe(res => {
      this.wizardForm.patchValue({ descripcion: res.descripcion });
      //this.step = 3;
    }, err => {
      console.error('Error generando descripción:', err);
    });
}

  // Paso 3: generar keywords
  onGenerateKeywords() {
  const id   = this.wizardForm.get('_id')!.value;
  const desc = this.wizardForm.get('descripcion')!.value || '';
  if (!id) {
    console.error('No hay ID de concepto para generar keywords');
    return;
  }
  this.conceptosService.generateKeywords(id, desc)
    .subscribe(res => {
      // tras generar los IDs, los traemos completos
      this.conceptosService.fetchKeywordsByConcept(id)
        .subscribe(list => {
          this.keywordsList = list;
          this.step = 3;
        });
    }, err => {
      console.error('Error generando keywords:', err);
    });
}

  addKeyword(name: string) {
    this.conceptosService
      .createKeyword(name)
      .subscribe((kw) => this.keywordsList.push(kw));
  }
  removeKeyword(i: number) {
    this.keywordsList.splice(i, 1);
  }

  // Paso 4: terminar y guardar associations
  finish() {
    const areaId = this.wizardForm.value.areaId;
    const keywordsRelacionadas: string[] = this.keywordsList.map((kw) => kw._id).filter((id): id is string => typeof id === 'string');
    
    const body = {
      _id: this.wizardForm.value._id,
      nombre: this.wizardForm.value.nombre,
      descripcion: this.wizardForm.value.descripcion,
      keywords_ids: keywordsRelacionadas,
    };
    this.conceptosService
      .acceptKeywords(areaId, body)
      .subscribe(() => this.crud.cancel());
  }

  onReview() {
    // Advance to step 4 (review step)
    this.step = 4;
  }
}
