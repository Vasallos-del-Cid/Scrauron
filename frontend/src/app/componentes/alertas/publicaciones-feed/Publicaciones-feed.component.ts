import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DropDownListModule } from '@syncfusion/ej2-angular-dropdowns';
import { DatePickerModule } from '@syncfusion/ej2-angular-calendars';
import { TextBoxModule } from '@syncfusion/ej2-angular-inputs';
import { PublicacionesService } from './publicaciones-feed.service';
import { Publicacion } from './publicacion.model';
import { MapaMundialComponent } from '../../mapa-mundial/mapa-mundial';
import { SpinnerComponent } from '../../../core/plantillas/spinner/spinner.component';
import { FuenteService } from '../../fuentes/fuentes.service';
import { ConceptosService } from '../../conceptos/conceptos.service';
import { map } from 'rxjs';
import { GraficoBarrasComponent } from '../../estadisticas/plot-chart-pub/plot-chart-pub.component';

@Component({
  selector: 'app-alertas-feed',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    DropDownListModule,
    DatePickerModule,
    TextBoxModule,
    SpinnerComponent,
    MapaMundialComponent,
    GraficoBarrasComponent
  ],
  templateUrl: './publicaciones-feed.component.html',
  styleUrls: ['./publicaciones-feed.component.css'],
})
export class PublicacionesFeedComponent implements OnInit {
  @ViewChild(MapaMundialComponent) mapaComponent!: MapaMundialComponent;

  public alertasFiltradas: Publicacion[] = [];
  public fuentesOpts: { id: string | null; nombre: string }[] = [];
  public conceptosOpts: { id: string | null; nombre: string }[] = [];
  public valoraciones = [
    { valor: null, nombre: 'Todos' },
    ...[1,2,3,4,5,6,7,8,9].map(n => ({ valor: n, nombre: n.toString() }))
  ];
  public filtroBusqueda = '';
  public filtroFuenteId: string | null = null;
  public filtroConceptoId: string | null = null;
  public filtroValoracion: number | null = null;
  public fechaDesde?: Date;
  public fechaHasta?: Date;
  public datosMapa: Record<string,number> = {};
  public expandidos = new Set<string>();
  public loading = false;
  public alertas: any[] = [];

  // Publicaciones por día y tono medio
  public datosPublicacionesDia: { datoX:string; datoY:number }[] = [];
  public datosTonoDia: { datoX:string; datoY:number }[] = [];
  public tituloGraficoPublicacionesDia = "Publicaciones por día";
  public ejeXPublicacionesDia = "Día";
  public ejeYPublicacionesDia = "Publicaciones";
  public tituloGraficoTonoDia = "Tono medio por día";
  public ejeXTonoDia = "Día";
  public ejeYTonoDia = "Tono";

  // Publicaciones por país y tono medio
  public datosPublicacionesPais: { datoX:string; datoY:number }[] = [];
  public datosTonoPais: { datoX:string; datoY:number }[] = [];
  public tituloGraficoPublicacionesPais = "Publicaciones por país";
  public ejeXPublicacionesPais = "País";
  public ejeYPublicacionesPais = "Publicaciones";
  public tituloGraficoTonoPais = "Tono medio por país";
  public ejeXTonoPais = "País";
  public ejeYTonoPais = "Tono";

  constructor(
    private servicio: PublicacionesService,
    private fuenteService: FuenteService,
    private conceptoService: ConceptosService
  ) {}

  ngOnInit(): void {
    this.fuenteService.getAll();
    this.conceptoService.getAll();

    // Inicializar fechas a hoy
    const hoy = new Date();
    this.fechaDesde = new Date(hoy);
    this.fechaHasta = new Date(hoy);

    // Ejecutar filtros iniciales
    this.aplicarFiltros();

    // Cargar opciones de filtros
    this.fuenteService.items$
      .pipe(map(list => [{ id: null, nombre: 'Todos' }, ...list.map(f => ({ id: f._id!, nombre: f.nombre }))]))
      .subscribe(opts => this.fuentesOpts = opts);

    this.conceptoService.items$
      .pipe(map(list => [{ id: null, nombre: 'Todos' }, ...list.map(c => ({ id: c._id!, nombre: c.nombre }))]))
      .subscribe(opts => this.conceptosOpts = opts);
  }

  aplicarFiltros(): void {
    // 1. Validar que fechas estén definidas
    if (!this.fechaDesde || !this.fechaHasta) {
      this.alertasFiltradas = [];
      return;
    }

    // 2. Normalizar rango de fechas
    const desde = new Date(this.fechaDesde);
    desde.setHours(2,1,0,0);
    const hasta = new Date(this.fechaHasta);
    hasta.setHours(25,59,0,0);

    this.loading = true; // 3. Mostrar spinner

    // 4. Llamar al servicio con filtros
    this.servicio.getFiltradas({
      fechaDesde: desde,
      fechaHasta: hasta,
      tono: this.filtroValoracion ?? undefined,
      busqueda_palabras: this.filtroBusqueda || undefined,
      fuente_id: this.filtroFuenteId || undefined,
      concepto_interes: this.filtroConceptoId || undefined,
    }).subscribe({
      next: (result: Publicacion[]) => {
        // 5. Mapear resultados y parsear fechas
        this.alertas = result.map(pub => ({
          ...pub,
          fecha: pub.fecha ? new Date(pub.fecha) : undefined,
          fuente: pub.fuente ?? undefined,
          conceptos_relacionados: pub.conceptos_relacionados || []
        }));
        this.alertasFiltradas = [...this.alertas];

        // 6. Generar datos para el mapa
        this.datosMapa = {};
        this.alertasFiltradas.forEach(a => {
          if (a.pais && a.pais.length === 3) {
            this.datosMapa[a.pais] = (this.datosMapa[a.pais] || 0) + 1;
          }
        });

        // 7. Generar dataset para gráficos mediante helpers
        this.datosPublicacionesPais = this.getPublicacionesPais();
        this.datosTonoPais = this.getTonoPais();
        this.datosPublicacionesDia = this.getPublicacionesDia();
        this.datosTonoDia = this.getTonoDia();

        // 8. Ocultar spinner
        this.loading = false;

        // 9. Actualizar componente del mapa
        setTimeout(() => {
          if (this.mapaComponent) {
            this.mapaComponent.dataPorPais = { ...this.datosMapa };
          }
        });
      },
      error: err => {
        console.error("Error al obtener publicaciones filtradas", err);
        this.alertas = [];
        this.alertasFiltradas = [];
        this.loading = false;
      }
    });
  }

  // --- Helpers para generación de datasets ---

  private getPublicacionesDia(): { datoX:string; datoY:number }[] {
    const conteo: Record<string,number> = {};
    this.alertasFiltradas.forEach(a => {
      if (a.fecha) {
        const d = a.fecha.toISOString().slice(0,10);
        conteo[d] = (conteo[d] || 0) + 1;
      }
    });
    return Object.entries(conteo)
      .map(([datoX, datoY]) => ({ datoX, datoY }))
      .sort((a,b) => a.datoX.localeCompare(b.datoX));
  }

  private getPublicacionesPais(): { datoX:string; datoY:number }[] {
    const conteo: Record<string,number> = {};
    this.alertasFiltradas.forEach(a => {
      if (a.pais) {
        conteo[a.pais] = (conteo[a.pais] || 0) + 1;
      }
    });
    return Object.entries(conteo)
      .map(([datoX, datoY]) => ({ datoX, datoY }))
      .sort((a,b) => a.datoX.localeCompare(b.datoX));
  }

  private getTonoDia(): { datoX:string; datoY:number }[] {
    const sums: Record<string,number> = {};
    const counts: Record<string,number> = {};
    this.alertasFiltradas.forEach(a => {
      if (a.fecha && a.tono != null) {
        const d = a.fecha.toISOString().slice(0,10);
        sums[d] = (sums[d] || 0) + a.tono;
        counts[d] = (counts[d] || 0) + 1;
      }
    });
    return Object.entries(sums)
      .map(([datoX, sum]) => ({ datoX, datoY: sum / counts[datoX] }))
      .sort((a,b) => a.datoX.localeCompare(b.datoX));
  }

  private getTonoPais(): { datoX:string; datoY:number }[] {
    const sums: Record<string,number> = {};
    const counts: Record<string,number> = {};
    this.alertasFiltradas.forEach(a => {
      if (a.pais && a.tono != null) {
        sums[a.pais] = (sums[a.pais] || 0) + a.tono;
        counts[a.pais] = (counts[a.pais] || 0) + 1;
      }
    });
    return Object.entries(sums)
      .map(([datoX, sum]) => ({ datoX, datoY: sum / counts[datoX] }))
      .sort((a,b) => a.datoX.localeCompare(b.datoX));
  }

  resetFiltros(): void {
    this.filtroBusqueda = '';
    this.filtroFuenteId = null;
    this.filtroConceptoId = null;
    this.filtroValoracion = null;
    const hoy = new Date();
    this.fechaDesde = new Date(hoy);
    this.fechaHasta = new Date(hoy);
    this.aplicarFiltros();
  }

  getColor(tono?: number): string {
    if (!tono || tono < 1 || tono > 10) return 'transparent';
    const t = (tono - 1) / 9;
    return `hsla(${Math.round(120 * t)}, 50%, 85%, 0.3)`;
  }

  toggleExpand(id: string): void {
    this.expandidos.has(id) ? this.expandidos.delete(id) : this.expandidos.add(id);
  }

  isExpanded(id: string): boolean {
    return this.expandidos.has(id);
  }
}
