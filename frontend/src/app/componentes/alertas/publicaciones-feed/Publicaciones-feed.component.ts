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
import { PAISES_EQUIVALENTES } from '../../../../environments/paises-equivalentes'



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



  //Oublicaciones filtradas
  public alertasFiltradas: Publicacion[] = [];

  //Opciones combos filtrado
  public fuentesOpts: { id: string | null; nombre: string }[] = [];
  public conceptosOpts: { id: string | null; nombre: string }[] = [];
  public valoraciones = [
    { valor: null, nombre: 'Todos' },
    ...[1, 2, 3, 4, 5, 6, 7, 8, 9].map(n => ({ valor: n, nombre: n.toString() }))
  ];

  //Filtros de búsqueda
  public filtroBusqueda = '';
  public filtroFuenteId: string | null = null;
  public filtroConceptoId: string | null = null;
  public filtroValoracion: number | null = null;
  public fechaDesde?: Date;
  public fechaHasta?: Date;

  public expandidos = new Set<string>();
  public alertas: any[] = [];

  //variable para spinner
  public loading = false;
  //Datos gráfica Publicaciones-Dia
  public datosPublicacionesDia: { datoX: string; datoY: number }[] = [];
  public tituloGraficoPublicacionesDia = "📰 Publicaciones por día 🗓️";
  public ejeXPublicacionesDia = "Día";
  public ejeYPublicacionesDia = "Publicaciones";

  //Datos gráfica Tono-Dia
  public datosTonoDia: { datoX: string; datoY: number }[] = [];
  public tituloGraficoTonoDia = "🌡️ Tono medio por día 🗓️";
  public ejeXTonoDia = "Día";
  public ejeYTonoDia = "Tono";

  //Datos gráfica Publicaciones-Pais
  public datosPublicacionesPais: { datoX: string; datoY: number }[] = [];
  public tituloGraficoPublicacionesPais = "📰 Publicaciones por país 🌍";
  public ejeXPublicacionesPais = "País";
  public ejeYPublicacionesPais = "Publicaciones";

  //Datos gráfica Tono-país
  public datosTonoPais: { datoX: string; datoY: number }[] = [];
  public tituloGraficoTonoPais = "🌡️ Tono medio por país 🌍";
  public ejeXTonoPais = "País";
  public ejeYTonoPais = "Tono";

  //Datos de las cajas del mapamundi
  public datosMapa: Record<string, number> = {};
  public totalPublicaciones: number = 0;
  public tonoMedioGeneral: number = 0;
  public paisConMasPublicaciones: string | null = null;

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

  aplicarFiltros(): void {
    if (!this.fechaDesde || !this.fechaHasta) {
      this.alertasFiltradas = [];
      return;
    }

    const desde = new Date(this.fechaDesde); desde.setHours(2, 1, 0, 0);
    const hasta = new Date(this.fechaHasta); hasta.setHours(25, 59, 0, 0);
    this.loading = true;

    this.servicio.getFiltradas({
      fechaDesde: desde,
      fechaHasta: hasta,
      tono: this.filtroValoracion ?? undefined,
      busqueda_palabras: this.filtroBusqueda || undefined,
      fuente_id: this.filtroFuenteId || undefined,
      concepto_interes: this.filtroConceptoId || undefined,
      pais: this.filtroPais || undefined // 👈 añadido
    }).subscribe({
      next: (result) => {
        this.alertas = result.map(pub => ({
          ...pub,
          fecha: pub.fecha ? new Date(pub.fecha) : undefined,
          fuente: pub.fuente ?? undefined,
          conceptos_relacionados: pub.conceptos_relacionados || []
        }));
        this.alertasFiltradas = [...this.alertas];

        this.datosMapa = {};
        let sumaTonos = 0;
        let cuentaTonos = 0;

        this.alertasFiltradas.forEach(a => {
          if (a.pais?.length === 3) {
            this.datosMapa[a.pais] = (this.datosMapa[a.pais] || 0) + 1;
          }
          if (a.tono != null) {
            sumaTonos += a.tono;
            cuentaTonos++;
          }
        });

        this.totalPublicaciones = this.alertasFiltradas.length;
        this.tonoMedioGeneral = cuentaTonos > 0 ? +(sumaTonos / cuentaTonos).toFixed(2) : 0;
        this.paisConMasPublicaciones = Object.entries(this.datosMapa)
          .reduce((max, curr) => curr[1] > max[1] ? curr : max, ["", 0])[0] || null;

        this.datosPublicacionesPais = this.getPublicacionesPais();
        this.datosTonoPais = this.getTonoPais();
        this.datosPublicacionesDia = this.getPublicacionesDia();
        this.datosTonoDia = this.getTonoDia();

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




  private normalizarNombrePais(nombreRaw: string): string {
    const n = nombreRaw.trim();
    const match = PAISES_EQUIVALENTES.find(p =>
      p.iso3.toLowerCase() === n.toLowerCase() ||
      p.ingles.toLowerCase() === n.toLowerCase() ||
      p.espanol.toLowerCase() === n.toLowerCase()
    );
    return match ? match.espanol : nombreRaw;
  }

  private getPublicacionesPais(): { datoX: string; datoY: number }[] {
    const conteo: Record<string, number> = {};
    this.alertasFiltradas.forEach(a => {
      if (a.pais) {
        const nom = this.normalizarNombrePais(a.pais);
        conteo[nom] = (conteo[nom] || 0) + 1;
      }
    });
    return Object.entries(conteo)
      .map(([datoX, datoY]) => ({ datoX, datoY }))
      .sort((a, b) => a.datoX.localeCompare(b.datoX));
  }

  private getTonoPais(): { datoX: string; datoY: number; conteo: number }[] {
    const sums: Record<string, number> = {}, counts: Record<string, number> = {};
    this.alertasFiltradas.forEach(a => {
      if (a.pais && a.tono != null) {
        const nom = this.normalizarNombrePais(a.pais);
        sums[nom] = (sums[nom] || 0) + a.tono;
        counts[nom] = (counts[nom] || 0) + 1;
      }
    });
    return Object.entries(sums)
      .map(([datoX, sum]) => ({
        datoX,
        datoY: +(sum / counts[datoX]).toFixed(2),
        conteo: counts[datoX]
      }))
      .sort((a, b) => a.datoX.localeCompare(b.datoX));
  }

  private getPublicacionesDia(): { datoX: string; datoY: number }[] {
    const conteo: Record<string, number> = {};
    this.alertasFiltradas.forEach(a => {
      if (a.fecha) {
        const d = a.fecha.toISOString().slice(0, 10);
        conteo[d] = (conteo[d] || 0) + 1;
      }
    });
    return Object.entries(conteo)
      .map(([datoX, datoY]) => ({ datoX, datoY }))
      .sort((a, b) => a.datoX.localeCompare(b.datoX));
  }

  private getTonoDia(): { datoX: string; datoY: number }[] {
    const sums: Record<string, number> = {}, counts: Record<string, number> = {};
    this.alertasFiltradas.forEach(a => {
      if (a.fecha && a.tono != null) {
        const d = a.fecha.toISOString().slice(0, 10);
        sums[d] = (sums[d] || 0) + a.tono;
        counts[d] = (counts[d] || 0) + 1;
      }
    });
    return Object.entries(sums)
      .map(([datoX, sum]) => ({ datoX, datoY: sum / counts[datoX] }))
      .sort((a, b) => a.datoX.localeCompare(b.datoX));
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
        a.download = 'informe_impacto.docx'; // Puedes cambiar el nombre si lo deseas
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


}

