import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DropDownListModule } from '@syncfusion/ej2-angular-dropdowns';
import { DatePickerModule } from '@syncfusion/ej2-angular-calendars';
import { TextBoxModule } from '@syncfusion/ej2-angular-inputs';
import { PublicacionesService } from './publicaciones-feed.service';
import { Publicacion } from './publicacion.model';
import { MapaMundialComponent } from '../../mapa-mundial/mapa-mundial';
import { PlotChartComponent } from '../../estadisticas/plot-chart/plot-chart.component';
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
    ...[1, 2, 3, 4, 5, 6, 7, 8, 9].map(n => ({ valor: n, nombre: n.toString() }))
  ];
  public filtroBusqueda = '';
  public filtroFuenteId: string | null = null;
  public filtroConceptoId: string | null = null;
  public filtroValoracion: number | null = null;
  public fechaDesde?: Date;
  public fechaHasta?: Date;
  public datosMapa: Record<string, number> = {};

  public expandidos = new Set<string>();
  public loading = false;
  public alertas: any[] = [];
  public datosPublicacionesDia: { datoX: string; datoY: number }[] = []; //X fecha e Y numero de publicaciones
  public tituloGraficoPublicacionesDia = "Publicaciones por dia"
  public ejeXPublicacionesDia = "Dia"
  public ejeYPublicacionesDia = "Publicaciones"

  public datosPublicacionesPais: { datoX: string; datoY: number }[] = []; //X pais e Y numero de publicaciones
  public tituloGraficoPublicacionesPais = "Publicaciones por país"
  public ejeXPublicacionesPais = "País"
  public ejeYPublicacionesPais = "Publicaciones"

  constructor(
    private servicio: PublicacionesService,
    private fuenteService: FuenteService,
    private conceptoService: ConceptosService
  ) { }

  ngOnInit(): void {
    this.fuenteService.getAll();
    this.conceptoService.getAll();

    this.fuenteService.items$
      .pipe(map(list => [{ id: null, nombre: 'Todos' }, ...list.map(f => ({ id: f._id!, nombre: f.nombre }))]))
      .subscribe(opts => (this.fuentesOpts = opts));

    this.conceptoService.items$
      .pipe(map(list => [{ id: null, nombre: 'Todos' }, ...list.map(c => ({ id: c._id!, nombre: c.nombre }))]))
      .subscribe(opts => (this.conceptosOpts = opts))
  }

  aplicarFiltros(): void {
    // Verifica que las fechas de filtro estén definidas
    if (!this.fechaDesde || !this.fechaHasta) {
      this.alertasFiltradas = [];
      return;
    }

    // Normaliza la hora de las fechas (esto ayuda a incluir el día completo)
    const desde = new Date(this.fechaDesde);
    desde.setHours(2, 1, 0, 0);
    const hasta = new Date(this.fechaHasta);
    hasta.setHours(25, 59, 0, 0); // 25h para asegurar cobertura completa del último día

    this.loading = true; // Activa el spinner

    // Llama al servicio para obtener las publicaciones filtradas según los criterios
    this.servicio.getFiltradas({
      fechaDesde: desde,
      fechaHasta: hasta,
      tono: this.filtroValoracion ?? undefined,
      busqueda_palabras: this.filtroBusqueda || undefined,
      fuente_id: this.filtroFuenteId || undefined,
      concepto_interes: this.filtroConceptoId || undefined,
    }).subscribe({
      next: (result: Publicacion[]) => {
        // Mapea cada publicación ajustando estructuras necesarias
        this.alertas = result.map(pub => ({
          ...pub,
          fecha: pub.fecha ? new Date(pub.fecha) : undefined,
          fuente: pub.fuente ?? undefined,
          conceptos_relacionados: pub.conceptos_relacionados || []
        }));

        // Copia de trabajo para filtrado
        this.alertasFiltradas = [...this.alertas];

        // ===============================
        // PUBLICACIONES POR PAÍS (para el mapa y gráfico)
        // ===============================
        this.datosMapa = {}; // Mapa: clave = país, valor = cantidad
        for (const alerta of this.alertasFiltradas) {
          if (alerta.pais && alerta.pais.length === 3) { // Solo códigos ISO válidos
            this.datosMapa[alerta.pais] = (this.datosMapa[alerta.pais] || 0) + 1;
          }
        }

        // También generar datos para gráfico por país
        const conteoPorPais: Record<string, number> = {};
        for (const alerta of this.alertasFiltradas) {
          if (alerta.pais) {
            conteoPorPais[alerta.pais] = (conteoPorPais[alerta.pais] || 0) + 1;
          }
        }
        this.datosPublicacionesPais = Object.entries(conteoPorPais)
          .map(([datoX, datoY]) => ({ datoX, datoY })) // Transformar en array de objetos
          .sort((a, b) => a.datoX.localeCompare(b.datoX)); // Orden alfabético por país

        // ===============================
        // PUBLICACIONES POR DÍA (para gráfico de barras)
        // ===============================
        const conteoPorFecha: Record<string, number> = {};
        for (const alerta of this.alertasFiltradas) {
          if (alerta.fecha) {
            const fechaStr = alerta.fecha.toISOString().slice(0, 10); // YYYY-MM-DD
            conteoPorFecha[fechaStr] = (conteoPorFecha[fechaStr] || 0) + 1;
          }
        }
        this.datosPublicacionesDia = Object.entries(conteoPorFecha)
          .map(([datoX, datoY]) => ({ datoX, datoY })) // Fecha y cantidad
          .sort((a, b) => a.datoX.localeCompare(b.datoX)); // Orden cronológico

        // Fin de la carga
        this.loading = false;

        // Actualiza el componente de mapa con los datos nuevos
        setTimeout(() => {
          if (this.mapaComponent) {
            this.mapaComponent.dataPorPais = { ...this.datosMapa };
          }
        }, 0);
      },
      error: (err) => {
        // Manejo de errores: limpia todo y apaga el spinner
        console.error("Error al obtener publicaciones filtradas", err);
        this.alertas = [];
        this.alertasFiltradas = [];
        this.loading = false;
      }
    });
  }


  resetFiltros(): void {
    this.filtroBusqueda = '';
    this.filtroFuenteId = null;
    this.filtroConceptoId = null;
    this.filtroValoracion = null;
    this.fechaDesde = undefined;
    this.fechaHasta = undefined;
    this.aplicarFiltros();
  }

  getColor(tono?: number): string {
    if (!tono || tono < 1 || tono > 10) return 'transparent';
    const t = (tono - 1) / 9;
    const hue = Math.round(120 * t);
    return `hsla(${hue}, 50%, 85%, 0.3)`;
  }

  toggleExpand(id: string): void {
    this.expandidos.has(id) ? this.expandidos.delete(id) : this.expandidos.add(id);
  }

  isExpanded(id: string): boolean {
    return this.expandidos.has(id);
  }
}
