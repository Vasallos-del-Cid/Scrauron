import { Routes } from '@angular/router';
import { BodyComponent } from './core/estructura/body/body.component';
import { ConceptosComponent } from './componentes/conceptos/conceptos.component';
import { FuentesComponent } from './componentes/fuentes/fuentes.component';
import { AreasComponent } from './componentes/areas/areas.component';
import { PerfilComponent } from './componentes/perfil/perfil.component';
import { NotFoundComponent } from './core/not-found/not-found.component';
import { PublicacionesFeedComponent } from './componentes/alertas/publicaciones-feed/Publicaciones-feed.component';


export const routes: Routes = [
  { path: '', component: BodyComponent },         // Home
  { path: 'conceptos', component: ConceptosComponent },
  { path: 'fuentes', component: FuentesComponent },
  { path: 'publicaciones', component: PublicacionesFeedComponent },
  { path: 'areas', component: AreasComponent },   // Cambia a AreasComponent
  { path: 'perfil', component: PerfilComponent },
  //{ path: 'login', component: LoginComponent },    // Si tienes login
  { path: '**', component: NotFoundComponent },    // Fallback para rutas no encontradas
];