import { Routes } from '@angular/router';
import { BodyComponent } from './core/estructura/body/body.component';
import { PruebaGridComponent } from './componentes/grid/prueba-grid/prueba-grid.component';

export const routes: Routes = [
  { path: '', component: BodyComponent },
  { path: 'grid', component: PruebaGridComponent },
];
