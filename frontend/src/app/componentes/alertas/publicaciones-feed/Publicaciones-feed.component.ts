import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChangeEventArgs, DropDownListModule } from '@syncfusion/ej2-angular-dropdowns';
import { DatePickerModule } from '@syncfusion/ej2-angular-calendars';
import { NumericTextBoxModule, TextBoxModule } from '@syncfusion/ej2-angular-inputs';
import { FormsModule } from '@angular/forms';
import { PublicacionesService } from './publicaciones-feed.service';
import { Publicacion } from './publicacion.model';
import { SpinnerComponent } from '../../../core/plantillas/spinner/spinner.component';

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
  public valoraciones: number[] = [1, 2, 3, 4, 5, 6, 7, 8, 9];
  public conceptos: any[] = [];
  public areas: any[] = [];
  public fuentes: any[] = [];
  public filtroBusqueda = '';
  public filtroFuente: string | null = null;
  public filtroValoracion: number | null = null;
  public filtroArea: string | null = null;
  public filtroConcepto: string | null = null;
  public fechaDesde: Date = new Date(new Date().setDate(new Date().getDate() - 1));
  public fechaHasta: Date = new Date();
  public expandidos = new Set<string>();
  public loading = true;

  constructor(private servicio: PublicacionesService) { }

  ngOnInit(): void {
    this.servicio.getAreas().subscribe({
      next: (areas) => {
        this.areas = areas;
      },
      error: (err) => {
        console.error('Error al cargar áreas:', err);
      }
    });
    this.servicio.getFuentes().subscribe({
      next: (fuentes) => {
        this.fuentes = fuentes;
      },
      error: (err) => {
        console.error('Error al cargar fuentes:', err);
      }
    });

    this.aplicarFiltros();
  }


  aplicarFiltros(e?: ChangeEventArgs) {
    if (!this.fechaDesde || !this.fechaHasta) return;

    this.loading = true;

    const filtros: any = {
      fechaDesde: this.fechaDesde,
      fechaHasta: this.fechaHasta,
      tono: this.filtroValoracion || undefined,
      busqueda_palabras: this.filtroBusqueda || undefined,
      concepto_interes: this.filtroConcepto || undefined,
      fuente_id: this.filtroFuente || undefined
    };

    if (!filtros.concepto_interes && this.filtroArea) {
      filtros.area_id = this.filtroArea;
    }

    this.servicio.getFiltradas(filtros).subscribe({
      next: (resultado) => {
        this.alertasFiltradas = resultado.map((pub) => ({
          ...pub,
          fecha: pub.fecha ? new Date(pub.fecha) : undefined

        }));
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al cargar publicaciones filtradas:', err);
        this.loading = false;
      }
    });
  }

  resetFiltros(): void {
    this.filtroBusqueda = '';
    this.filtroFuente = null;
    this.filtroValoracion = null;
    this.filtroArea = null;
    this.filtroConcepto = null;
    this.fechaDesde = new Date(new Date().setDate(new Date().getDate() - 7));
    this.fechaHasta = new Date();
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
