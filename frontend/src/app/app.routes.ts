import { Routes } from '@angular/router';
import { BodyComponent } from './core/estructura/body/body.component';
import { InteresesComponent } from './componentes/intereses/intereses.component';
import { FuentesComponent } from './componentes/fuentes/fuentes.component';
import { AreasComponent } from './componentes/areas/areas.component';
import { PerfilComponent } from './componentes/perfil/perfil.component';
import { NotFoundComponent } from './core/not-found/not-found.component';
import { AlertasFeedComponent } from './componentes/alertas/alertas-feed/alertas-feed.component';

export const routes: Routes = [
  { path: '', component: BodyComponent },         // Home
  { path: 'intereses', component: InteresesComponent },
  { path: 'fuentes', component: FuentesComponent },
  { path: 'alertas', component: AlertasFeedComponent },
  { path: 'areas', component: AreasComponent },   // Cambia a AreasComponent
  { path: 'perfil', component: PerfilComponent },
  //{ path: 'login', component: LoginComponent },    // Si tienes login
  { path: '**', component: NotFoundComponent },    // Fallback para rutas no encontradas
];