import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DropDownListModule } from '@syncfusion/ej2-angular-dropdowns';
import { DatePickerModule } from '@syncfusion/ej2-angular-calendars';
import { TextBoxModule } from '@syncfusion/ej2-angular-inputs';
import { FormsModule } from '@angular/forms';
import { PublicacionesService } from './alertas-feed.service';
import { Publicacion } from './publicacion.model';

@Component({
  selector: 'app-alertas-feed',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    DropDownListModule,
    DatePickerModule,
    TextBoxModule,
  ],
  templateUrl: './alertas-feed.component.html',
  styleUrls: ['./alertas-feed.component.css'],
})
export class AlertasFeedComponent implements OnInit {
  public alertas: Publicacion[] = [];
  public alertasFiltradas: Publicacion[] = [];

  public fuentes: string[] = ['Todos'];
  public valoraciones: number[] = [0, 1, 2, 3];

  public filtroBusqueda = '';
  public filtroFuente = 'Todos';
  public filtroValoracion = 0;
  public fechaDesde?: Date;
  public fechaHasta?: Date;

  public expandidos = new Set<string>();

  constructor(private servicio: PublicacionesService) {}

  ngOnInit(): void {
    // 1) Lanza la petición
    this.servicio.getAll({ silent: true });

    // 2) Suscríbete al BehaviorSubject y transforma fecha a Date
    this.servicio.items$.subscribe((list) => {
      this.alertas = list.map((pub) => ({
        ...pub,
        fecha: pub.fecha ? new Date(pub.fecha) : undefined,
      }));
      // Extrae fuentes únicas para el filtro
      const setFuentes = new Set(this.alertas.map((a) => a.fuente || ''));
      this.fuentes = ['Todos', ...Array.from(setFuentes)];
      this.aplicarFiltros();
    });
  }

  aplicarFiltros(): void {
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
        this.filtroValoracion === 0 || a.tono === this.filtroValoracion;

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
    if (tono === 1) return 'verde'; // positivo
    if (tono === 3) return 'rojo'; // negativo
    return ''; // neutro o sin tono
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
