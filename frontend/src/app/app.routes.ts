import { Routes } from '@angular/router';
import { ConceptosComponent } from './componentes/conceptos/conceptos.component';
import { FuentesComponent } from './componentes/fuentes/fuentes.component';
import { AreasComponent } from './componentes/areas/areas.component';
import { PerfilComponent } from './componentes/perfil/perfil.component';
import { NotFoundComponent } from './core/not-found/not-found.component';
import { PublicacionesFeedComponent } from './componentes/alertas/publicaciones-feed/Publicaciones-feed.component';
import { HomeComponent } from './core/estructura/home/home.component';
import { MultiLineaComponent } from './componentes/estadisticas/multi-linea/multi-linea.component';
import { BarChartComponent } from './componentes/estadisticas/bar-chart/bar-chart.component';
import { PlotChartComponent } from './componentes/estadisticas/plot-chart/plot-chart.component';

export const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent }, // Home
  { path: 'multilinea', component: MultiLineaComponent },
  { path: 'barchart', component: BarChartComponent },
  { path: 'plotchart', component: PlotChartComponent }, // Asegúrate de que PlotChartComponent esté importado
  { path: 'conceptos', component: ConceptosComponent },
  { path: 'fuentes', component: FuentesComponent },
  { path: 'publicaciones', component: PublicacionesFeedComponent },
  { path: 'areas', component: AreasComponent }, // Cambia a AreasComponent
  { path: 'perfil', component: PerfilComponent },
  //{ path: 'login', component: LoginComponent },    // Si tienes login
  { path: '**', component: NotFoundComponent }, // Fallback para rutas no encontradas
];
