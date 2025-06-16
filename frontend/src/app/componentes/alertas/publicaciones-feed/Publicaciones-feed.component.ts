import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChangeEventArgs, DropDownListModule } from '@syncfusion/ej2-angular-dropdowns';
import { DatePickerModule } from '@syncfusion/ej2-angular-calendars';
import { NumericTextBoxModule, TextBoxModule } from '@syncfusion/ej2-angular-inputs';
import { FormsModule } from '@angular/forms';
import { PublicacionesService } from './publicaciones-feed.service';
import { Publicacion } from './publicacion.model';

import { map } from 'rxjs';
import { SpinnerComponent } from '../../../core/plantillas/spinner/spinner.component';
import { FuenteService } from '../../fuentes/fuentes.service';
import { ConceptosService } from '../../conceptos/conceptos.service';
import { Fuente } from '../../fuentes/fuente.model';
import { Conceptos } from '../../conceptos/Conceptos.model';

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
  ],
  templateUrl: './publicaciones-feed.component.html',
  styleUrls: ['./publicaciones-feed.component.css'],
})
export class PublicacionesFeedComponent implements OnInit {
  public alertasFiltradas: Publicacion[] = [];

  // dropdowns vacíos hasta cargar del back
  public fuentesOpts: { id: string|null; nombre: string }[] = [];
  public conceptosOpts: { id: string|null; nombre: string }[] = [];


  public valoraciones = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  public filtroBusqueda = '';
  public filtroFuenteId: string|null = null;
  public filtroConceptoId: string|null = null;
  public filtroValoracion: number | null = null;
  public fechaDesde?: Date;
  public fechaHasta?: Date;

  public expandidos = new Set<string>();
  public loading = true;

  constructor(
    private servicio: PublicacionesService,
    private fuenteService: FuenteService,
    private conceptoService: ConceptosService
  ) {}

  ngOnInit(): void {
    // 1) Cargo los maestros
    this.fuenteService.getAll();
    this.conceptoService.getAll();

    // 2) Suscribo fuentes para llenar el dropdown
     this.fuenteService.items$
      .pipe(
        map(list => [
          { id: null, nombre: 'Todos' },
          ...list.map(f => ({ id: f._id!, nombre: f.nombre }))
        ])
      )
      .subscribe(opts => (this.fuentesOpts = opts));

    // 3️⃣ Mapea conceptos igual
    this.conceptoService.items$
      .pipe(
        map(list => [
          { id: null, nombre: 'Todos' },
          ...list.map(c => ({ id: c._id!, nombre: c.nombre }))
        ])
      )
      .subscribe(opts => (this.conceptosOpts = opts));

    // 4) Cargo y filtro publicaciones
    this.servicio.getAll();
    this.servicio.items$
      .pipe(
        // filtrado previo de contenido/tono
        map((list) =>
          list.filter(
            (pub) => pub.contenido?.trim().length! > 0 && pub.tono != null
          )
        ),
        // parseo fecha
        map((list) =>
          list.map((pub) => ({
            ...pub,
            fecha: pub.fecha ? new Date(pub.fecha) : undefined,
          }))
        )
      )
      .subscribe((list) => {
        this.alertas = list;
        this.aplicarFiltros();
        this.loading = false;
      });
  }

  onFuenteChange(e: ChangeEventArgs) {
    this.filtroFuenteId = e.value as string|null;
    this.aplicarFiltros();
  }

  /** Lectura manual del dropdown de conceptos */
  onConceptoChange(e: ChangeEventArgs) {
    this.filtroConceptoId = e.value as string|null;
    this.aplicarFiltros();
  }

  aplicarFiltros(): void {
    this.alertasFiltradas = this.alertas.filter((a) => {
      const texto = this.filtroBusqueda.toLowerCase();
      const okBusqueda =
        !this.filtroBusqueda ||
        a.titulo.toLowerCase().includes(texto) ||
        (a.contenido?.toLowerCase().includes(texto) ?? false);
      const okFuente =
        this.filtroFuenteId === null ||
        a.fuente?._id === this.filtroFuenteId;
      const okConcepto =
        this.filtroConceptoId === null ||
        a.conceptos_relacionados.some(c => c._id === this.filtroConceptoId);
      const okValoracion =
        this.filtroValoracion == null || a.tono === this.filtroValoracion;
      const okDesde =
        !this.fechaDesde || (a.fecha && a.fecha >= this.fechaDesde);
      const okHasta =
        !this.fechaHasta || (a.fecha && a.fecha <= this.fechaHasta);

      return (
        okBusqueda &&
        okFuente &&
        okConcepto &&
        okValoracion &&
        okDesde &&
        okHasta
      );
    });
  }

  resetFiltros(): void {
    this.filtroBusqueda = '';
    this.filtroFuenteId = null;
    this.filtroConceptoId = null;
    this.filtroValoracion = 0;
    this.fechaDesde = undefined;
    this.fechaHasta = undefined;
    this.aplicarFiltros();
  }

  getColor(tono?: number): string {
    if (!tono || tono < 1 || tono > 10) {
      return 'transparent';
    }
    const t = (tono - 1) / 9;
    const hue = Math.round(120 * t);
    return `hsla(${hue}, 50%, 85%, 0.3)`;
  }

  toggleExpand(id: string): void {
    if (this.expandidos.has(id)) {
      this.expandidos.delete(id);
    } else {
      this.expandidos.add(id);
    }
  }

  isExpanded(id: string): boolean {
    return this.expandidos.has(id);
  }

  onAreaChange(areaId: string): void {
    this.filtroArea = areaId;
    this.servicio.getConceptosArea(areaId).subscribe({
      next: (conceptos) => {
        this.conceptos = conceptos;
      },
      error: (err) => {
        console.error('Error al cargar conceptos del área:', err);
      }
    });
  }

  onConceptoChange(conceptoId: string): void {
    this.filtroConcepto = conceptoId;
    this.aplicarFiltros();
  }



}
