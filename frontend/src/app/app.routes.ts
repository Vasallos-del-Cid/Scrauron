import { Routes } from '@angular/router';
import { BodyComponent } from './core/estructura/body/body.component';
import { PruebaGridComponent } from './componentes/grid/prueba-grid/prueba-grid.component';
import { InteresesComponent } from './componentes/intereses/intereses.component';
import { FuentesComponent } from './componentes/fuentes/fuentes.component';
import { AlertasComponent } from './componentes/alertas/alertas.component';
import { PerfilComponent } from './componentes/perfil/perfil.component';
import { NotFoundComponent } from './core/not-found/not-found.component';

export const routes: Routes = [
  { path: '', component: BodyComponent },         // Home
  { path: 'grid', component: PruebaGridComponent },// (esto lo puedes quitar si ya no usas grid de prueba)
  { path: 'intereses', component: InteresesComponent },
  { path: 'fuentes', component: FuentesComponent },
  { path: 'alertas', component: AlertasComponent },
  { path: 'perfil', component: PerfilComponent },
  //{ path: 'login', component: LoginComponent },    // Si tienes login
  { path: '**', component: NotFoundComponent },    // Fallback para rutas no encontradas
];