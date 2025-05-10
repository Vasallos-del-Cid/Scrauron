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
} from '@angular/forms';
import { SwitchModule } from '@syncfusion/ej2-angular-buttons';

@Component({
  selector: 'app-form-crear-fuentes',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, SwitchModule],
  templateUrl: './form-crear-fuentes.component.html',
  styleUrls: ['./form-crear-fuentes.component.css'],
})
export class FormCrearFuentesComponent implements OnChanges {
  @Output() guardar = new EventEmitter<any>();
  @Output() cancelar = new EventEmitter<void>();
  @Input() fuente: any = null; // 👈 Recibimos la fuente a editar

  fuenteForm: FormGroup;

  constructor(private fb: FormBuilder) {
    this.fuenteForm = this.fb.group({
      nombre: ['', Validators.required],
      tipo: [''],
      url: ['', [Validators.required, Validators.pattern('https?://.+')]],
      activa: [true],
      fecha_alta: [new Date().toISOString().split('T')[0]],
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['fuente'] && this.fuente) {
      this.fuenteForm.patchValue(this.fuente);
    } else {
      this.fuenteForm.reset({
        activa: true,
        fecha_alta: new Date().toISOString().split('T')[0],
      });
    }
  }

  submitForm() {
    if (this.fuenteForm.valid) {
      this.guardar.emit(this.fuenteForm.value);
    }
  }

  campoInvalido(campo: string): boolean {
    const control = this.fuenteForm.get(campo);
    return !!(control && control.invalid && control.touched);
  }

  cancelarForm() {
    this.cancelar.emit();
  }
}
