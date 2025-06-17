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
    MapaMundialComponent
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
      .subscribe(opts => (this.conceptosOpts = opts));


  }

  aplicarFiltros(): void {
    if (!this.fechaDesde || !this.fechaHasta) {
      this.alertasFiltradas = [];
      return;
    }

    const desde = new Date(this.fechaDesde);
    desde.setHours(2, 1, 0, 0);
    const hasta = new Date(this.fechaHasta);
    hasta.setHours(25, 59, 0, 0);

    this.loading = true;

    this.servicio.getFiltradas({
      fechaDesde: desde,
      fechaHasta: hasta,
      tono: this.filtroValoracion ?? undefined,
      busqueda_palabras: this.filtroBusqueda || undefined,
      fuente_id: this.filtroFuenteId || undefined,
      concepto_interes: this.filtroConceptoId || undefined,
    }).subscribe({
      next: (result: Publicacion[]) => {
        this.alertas = result.map(pub => ({
          ...pub,
          fecha: pub.fecha ? new Date(pub.fecha) : undefined,
          fuente: pub.fuente ?? undefined,
          conceptos_relacionados: pub.conceptos_relacionados || []
        }));
        this.alertasFiltradas = [...this.alertas];

        this.datosMapa = {};
        for (const alerta of this.alertasFiltradas) {
          if (alerta.pais && alerta.pais.length === 3) {
            this.datosMapa[alerta.pais] = (this.datosMapa[alerta.pais] || 0) + 1;
          }
        }

        this.loading = false;

        setTimeout(() => {
          if (this.mapaComponent) {
            this.mapaComponent.dataPorPais = { ...this.datosMapa };
          }
        }, 0);
      },
      error: (err) => {
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
