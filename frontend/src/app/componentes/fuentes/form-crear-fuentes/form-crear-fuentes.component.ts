import {
  Component,
  EventEmitter,
  Output,
  Input,
  OnChanges,
  SimpleChanges,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
  FormsModule,
} from '@angular/forms';
import { SwitchModule } from '@syncfusion/ej2-angular-buttons';
import { Fuente } from '../fuente.model';
import { DropDownListModule } from '@syncfusion/ej2-angular-dropdowns';

@Component({
  selector: 'app-form-crear-fuentes',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    SwitchModule,
    FormsModule,
    ReactiveFormsModule,
    DropDownListModule,
  ],
  templateUrl: './form-crear-fuentes.component.html',
  styleUrls: ['./form-crear-fuentes.component.css'],
})
export class FormCrearFuentesComponent implements OnChanges {
  //parametros de entrada y salida por el html
  @Output() guardar = new EventEmitter<any>();
  @Output() cancelar = new EventEmitter<void>();
  @Input() fuente?: Fuente; // 👈 Recibimos la fuente a editar

  fuenteForm: FormGroup;

  public tiposFuente: string[] = [
    'Blog',
    'Noticias',
    'Investigación',
    'Social',
    'Otro',
  ];

  constructor(private fb: FormBuilder) {
    this.fuenteForm = this.fb.group({
      nombre: ['', Validators.required],
      tipo: [''],
      url: [
        '',
        [Validators.required, Validators.pattern('^(http://|https://).+')],
      ],
      activa: [true],
      fecha_alta: [new Date().toISOString()],
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['fuente'] && this.fuente) {
      this.fuenteForm.patchValue(this.fuente);
    } else {
      this.fuenteForm.reset({
        activa: true,
        fecha_alta: new Date().toISOString(),
      });
    }
  }

  submitForm() {
    if (this.fuenteForm.valid) {
      const formValue = this.fuenteForm.value;
      if (!formValue.fecha_alta) {
        formValue.fecha_alta = new Date().toISOString();
      }
      if (this.fuente && this.fuente._id) {
        formValue._id = this.fuente._id;
      }
      this.guardar.emit(formValue);
      this.fuente = undefined; // Limpiamos la fuente después de guardar
    }
  }

  campoInvalido(campo: string): boolean {
    const control = this.fuenteForm.get(campo);
    return !!(control && control.invalid && control.touched);
  }

  cancelarForm() {
    this.fuenteForm.reset(); // Limpia valores anteriores
    this.cancelar.emit();
  }
}
