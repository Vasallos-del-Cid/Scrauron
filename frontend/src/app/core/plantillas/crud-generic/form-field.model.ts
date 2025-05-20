
import { ValidatorFn } from '@angular/forms';
export interface FormFieldConfig {
  name: string;            // formControlName
  label: string;
  type: 'text'|'switch'|'date'|'number'|'select';
  validators?: ValidatorFn[];
  options?: { value: any; label: string }[]; // para selects
  placeholder?: string;
}
