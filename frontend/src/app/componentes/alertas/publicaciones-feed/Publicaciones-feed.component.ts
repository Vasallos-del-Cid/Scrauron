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
  public alertas: Publicacion[] = [];
  public alertasFiltradas: Publicacion[] = [];

  public fuentes: string[] = ['Todos'];
  public valoraciones: number[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  public filtroBusqueda = '';
  public filtroFuente = 'Todos';
  public filtroValoracion:number|null = null;
  public fechaDesde?: Date;
  public fechaHasta?: Date;

  public expandidos = new Set<string>();
  public loading = true;

  constructor(private servicio: PublicacionesService) {}

  ngOnInit(): void {
    // 1) Lanza la petición
    this.servicio.getAll();

    // 2) Suscríbete al BehaviorSubject y transforma fecha a Date
    this.servicio.items$
      .pipe(
        // 2.1) Filtra out los que no tienen contenido o tono vacío/undefined
        map((list) =>
          list.filter(
            (pub) => pub.contenido?.trim().length! > 0 && pub.tono != null
          )
        ),
        // 2.2) Convierte fecha a Date y lo que necesites
        map((list) =>
          list.map((pub) => ({
            ...pub,
            fecha: pub.fecha ? new Date(pub.fecha) : undefined,
          }))
        )
      )
      .subscribe((list) => {
        this.alertas = list.map((pub) => ({
          ...pub,
          fecha: pub.fecha ? new Date(pub.fecha) : undefined,
        }));
        // Extrae fuentes únicas para el filtro
        const setFuentes = new Set(this.alertas.map((a) => a.fuente || ''));
        this.fuentes = ['Todos', ...Array.from(setFuentes)];
        this.aplicarFiltros();
        if (this.alertas.length > 0) { 
          this.loading = false;
        }
      });
  }

  aplicarFiltros(e?: ChangeEventArgs) {
    this.alertasFiltradas = this.alertas.filter((a) => {
      const titulo = a.titulo.toLowerCase();
      const contenido = (a.contenido || '').toLowerCase();
      const texto = this.filtroBusqueda.toLowerCase();

      const okBusqueda =
        !this.filtroBusqueda ||
        titulo.includes(texto) ||
        contenido.includes(texto);

      const okFuente =
        this.filtroFuente === 'Todos' || a.fuente === this.filtroFuente;

      const okValoracion =
        this.filtroValoracion == null || a.tono == this.filtroValoracion;

      const okDesde =
        !this.fechaDesde || (a.fecha != null && a.fecha >= this.fechaDesde);

      const okHasta =
        !this.fechaHasta || (a.fecha != null && a.fecha <= this.fechaHasta);

      return okBusqueda && okFuente && okValoracion && okDesde && okHasta;
    });
  }

  resetFiltros(): void {
    this.filtroBusqueda = '';
    this.filtroFuente = 'Todos';
    this.filtroValoracion = 0;
    this.fechaDesde = undefined;
    this.fechaHasta = undefined;
    this.aplicarFiltros();
  }

  /** Mapea el tono numérico a una clase CSS */
  getColor(tono?: number): string {
    if (!tono || tono < 1 || tono > 10) {
      // neutro / sin color
      return 'transparent';
    }
    // normalizamos entre 0 y 1
    const t = (tono - 1) / 9;
    // mapeamos a hue (0 = rojo; 120 = verde)
    const hue = Math.round(120 * t);
    // saturación baja (50%), luminosidad alta (85%), alpha suave (0.3)
    return `hsla(${hue}, 50%, 85%, 0.3)`;
  }

  /** Alterna el estado expandido de una alerta */
  toggleExpand(id: string): void {
    if (this.expandidos.has(id)) {
      this.expandidos.delete(id);
    } else {
      this.expandidos.add(id);
    }
  }

  /** Consulta si está expandida */
  isExpanded(id: string): boolean {
    return this.expandidos.has(id);
  }
}
