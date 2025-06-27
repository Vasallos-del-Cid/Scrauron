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
import { PAISES_EQUIVALENTES } from '../../../../environments/paises-equivalentes';

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

  public filtroPais: string | null = null;
  public listaPaises = [
    { codigo: null, nombre: 'Todos' }, { codigo: 'indeterminado', nombre: 'Indeterminado' },
    ...PAISES_EQUIVALENTES
      .map(p => ({ codigo: p.iso3, nombre: p.espanol }))
      .sort((a, b) => a.nombre.localeCompare(b.nombre))
  ];

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

  public expandidos = new Set<string>();
  public alertas: any[] = [];
  public loading = false;

  public datosPublicacionesDia: { datoX: string; datoY: number }[] = [];
  public tituloGraficoPublicacionesDia = "📰 Publicaciones por día 🗓️";
  public ejeXPublicacionesDia = "Día";
  public ejeYPublicacionesDia = "Publicaciones";

  public datosTonoDia: { datoX: string; datoY: number }[] = [];
  public tituloGraficoTonoDia = "🌡️ Tono medio por día 🗓️";
  public ejeXTonoDia = "Día";
  public ejeYTonoDia = "Tono";

  public datosPublicacionesPais: { datoX: string; datoY: number }[] = [];
  public tituloGraficoPublicacionesPais = "📰 Publicaciones por país 🌍";
  public ejeXPublicacionesPais = "País";
  public ejeYPublicacionesPais = "Publicaciones";

  public datosTonoPais: { datoX: string; datoY: number }[] = [];
  public tituloGraficoTonoPais = "🌡️ Tono medio por país 🌍";
  public ejeXTonoPais = "País";
  public ejeYTonoPais = "Tono";

  public datosMapa: Record<string, number> = {};
  public totalPublicaciones: number = 0;
  public tonoMedioGeneral: number = 0;
  public paisConMasPublicaciones: string | null = null;

  public paginaActual = 1;
  public publicacionesPorPagina = 25;
  public totalFiltradas = 0;

  constructor(
    private servicio: PublicacionesService,
    private fuenteService: FuenteService,
    private conceptoService: ConceptosService
  ) { }

  ngOnInit(): void {
    this.fuenteService.getAll();
    this.conceptoService.getAll();

    const hoy = new Date();
    this.fechaDesde = new Date(hoy);
    this.fechaHasta = new Date(hoy);
    this.aplicarFiltros();

    this.fuenteService.items$
      .pipe(map(list => [{ id: null, nombre: 'Todos' }, ...list.map(f => ({ id: f._id!, nombre: f.nombre }))]))
      .subscribe(opts => this.fuentesOpts = opts);

    this.conceptoService.items$
      .pipe(map(list => [{ id: null, nombre: 'Todos' }, ...list.map(c => ({ id: c._id!, nombre: c.nombre }))]))
      .subscribe(opts => this.conceptosOpts = opts);
  }

  aplicarFiltrosNuevaConsulta(): void {
    this.paginaActual=1
    this.aplicarFiltros()
  }

  aplicarFiltros(): void {
    if (!this.fechaDesde || !this.fechaHasta) {
      this.alertasFiltradas = [];
      return;
    }

    const desde = new Date(this.fechaDesde); desde.setHours(2, 1, 0, 0);
    const hasta = new Date(this.fechaHasta); hasta.setHours(25, 59, 0, 0);
    this.loading = true;

    const filtros = {
      fechaDesde: desde,
      fechaHasta: hasta,
      tono: this.filtroValoracion ?? undefined,
      busqueda_palabras: this.filtroBusqueda || undefined,
      fuente_id: this.filtroFuenteId || undefined,
      concepto_interes: this.filtroConceptoId || undefined,
      pais: this.filtroPais || undefined,
      page: this.paginaActual,
      pageSize: this.publicacionesPorPagina
    };

    this.servicio.getFiltradas(filtros).subscribe({
      next: (result) => {
        this.totalFiltradas = result.total;
        this.alertas = result.publicaciones.map(pub => ({
          ...pub,
          fecha: pub.fecha ? new Date(pub.fecha) : undefined,
          fuente: pub.fuente ?? undefined,
          conceptos_relacionados: pub.conceptos_relacionados || []
        }));
        this.alertasFiltradas = [...this.alertas];

        const params: any = {
          fechaInicio: this.toLocalIsoString(desde),
          fechaFin: this.toLocalIsoString(hasta)
        };

        if (this.filtroValoracion != null) params.tono = this.filtroValoracion;
        if (this.filtroBusqueda) params.busqueda_palabras = this.filtroBusqueda;
        if (this.filtroFuenteId) params.fuente_id = this.filtroFuenteId;
        if (this.filtroConceptoId) params.concepto_interes = this.filtroConceptoId;
        if (this.filtroPais) params.pais = this.filtroPais;

        this.servicio.getPublicacionesPorDia(params).subscribe(d => this.datosPublicacionesDia = d);
        this.servicio.getTonoMedioPorDia(params).subscribe(d => this.datosTonoDia = d);

        this.servicio.getPublicacionesPorPais(params).subscribe(d => {
          this.datosMapa = d.reduce((acc, cur) => ({ ...acc, [cur.datoX]: cur.datoY }), {});
          this.totalPublicaciones = d.reduce((sum, item) => sum + item.datoY, 0);
          const maxPais = d.reduce((prev, curr) => curr.datoY > prev.datoY ? curr : prev, { datoX: '', datoY: 0 });
          this.paisConMasPublicaciones = maxPais?.datoX || null;

          this.datosPublicacionesPais = d.map(p => ({
            datoX: this.normalizarNombrePais(p.datoX),
            datoY: p.datoY
          }));
        });

        this.servicio.getTonoMedioPorPais(params).subscribe(d => {
          this.datosTonoPais = d.map(p => ({
            datoX: this.normalizarNombrePais(p.datoX),
            datoY: p.datoY
          }));
          const totalPeso = d.reduce((sum, item) => sum + item.datoY, 0);
          this.tonoMedioGeneral = d.length > 0 ? +(totalPeso / d.length).toFixed(2) : 0;
        });

        this.loading = false;

        setTimeout(() => {
          if (this.mapaComponent) {
            this.mapaComponent.dataPorPais = { ...this.datosMapa };
          }
        }, 0);
      },
      error: (err) => {
        console.error(err);
        this.alertas = [];
        this.alertasFiltradas = [];
        this.loading = false;
      }
    });
  }

  private toLocalIsoString(date: Date): string {
    const pad = (n: number) => n.toString().padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  }

  private normalizarNombrePais(nombreRaw: string): string {
    const n = nombreRaw.trim();
    const match = PAISES_EQUIVALENTES.find(p =>
      p.iso3.toLowerCase() === n.toLowerCase() ||
      p.ingles.toLowerCase() === n.toLowerCase() ||
      p.espanol.toLowerCase() === n.toLowerCase()
    );
    return match ? match.espanol : nombreRaw;
  }

  resetFiltros(): void {
    this.filtroBusqueda = '';
    this.filtroFuenteId = null;
    this.filtroConceptoId = null;
    this.filtroValoracion = null;
    this.filtroPais = null;
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

  confirmarEliminarConcepto(pubId: string, conceptoId: string, nombre: string): void {
    const confirmar = confirm(`¿Quiere desvincular esta publicación del concepto "${nombre}"?`);
    if (confirmar) {
      this.servicio.eliminarConcepto(pubId, conceptoId).subscribe({
        next: () => this.aplicarFiltros(),
        error: err => console.error('Error eliminando concepto:', err)
      });
    }
  }

  public nombrePais(alerta: Publicacion): string {
    return alerta.pais ? this.normalizarNombrePais(alerta.pais) : '';
  }

  generarInformeImpactoTemporal(): void {
    if (!this.fechaDesde || !this.fechaHasta) return;

    const desde = new Date(this.fechaDesde); desde.setHours(2, 1, 0, 0);
    const hasta = new Date(this.fechaHasta); hasta.setHours(25, 59, 0, 0);

    let params = {
      fechaDesde: desde,
      fechaHasta: hasta,
      tono: this.filtroValoracion ?? undefined,
      busqueda_palabras: this.filtroBusqueda || undefined,
      fuente_id: this.filtroFuenteId || undefined,
      concepto_interes: this.filtroConceptoId || undefined,
      pais: this.filtroPais || undefined
    };

    this.loading = true;
    this.servicio.generarInformeImpactoTemporal(params).subscribe({
      next: (blob: Blob) => {
        this.loading = false;
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'informe_impacto.docx';
        a.click();
        window.URL.revokeObjectURL(url);
        console.log("Informe descargado con éxito.");
      },
      error: (err) => {
        this.loading = false;
        console.error("Error al generar el informe:", err);
      }
    });
  }

  paginaAnterior(): void {
    if (this.paginaActual > 1) {
      this.paginaActual--;
      this.aplicarFiltros();
    }
  }

  paginaSiguiente(): void {
    if ((this.paginaActual * this.publicacionesPorPagina) < this.totalFiltradas) {
      this.paginaActual++;
      this.aplicarFiltros();
    }
  }
}
