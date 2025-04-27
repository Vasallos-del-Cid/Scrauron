import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DropDownListModule } from '@syncfusion/ej2-angular-dropdowns';
import { DatePickerModule } from '@syncfusion/ej2-angular-calendars';
import { TextBoxModule } from '@syncfusion/ej2-angular-inputs';
import { FormsModule } from '@angular/forms'; // Para [(ngModel)]
import { ALERTAS_MOCK } from './alertas-mock'; // Asegúrate de que la ruta sea correcta

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
  public alertas: any[] = [];
  public alertasFiltradas: any[] = [];

  public intereses: string[] = ['Todos', 'Wilkinson', 'Crisis', 'Publicidad'];
  public fuentes: string[] = ['Todos', 'Twitter', 'Telegram', 'Prensa'];
  public valoraciones: string[] = ['Todos', 'Buena', 'Regular', 'Mala'];

  public filtroBusqueda: string = '';
  public filtroInteres: string = 'Todos';
  public filtroFuente: string = 'Todos';
  public filtroValoracion: string = 'Todos';
  public filtroImpacto: number = 0;
  public fechaDesde?: Date;
  public fechaHasta?: Date;

  constructor() {}

  ngOnInit(): void {
    this.cargarAlertasMock();
    this.aplicarFiltros();
  }

  cargarAlertasMock(): void {
    this.alertas = ALERTAS_MOCK
  }

  aplicarFiltros(): void {
    this.alertasFiltradas = this.alertas.filter((alerta) => {
      const coincideBusqueda =
        this.filtroBusqueda === '' ||
        alerta.titulo
          .toLowerCase()
          .includes(this.filtroBusqueda.toLowerCase()) ||
        alerta.resumen
          .toLowerCase()
          .includes(this.filtroBusqueda.toLowerCase());

      const coincideInteres =
        this.filtroInteres === 'Todos' ||
        alerta.intereses.includes(this.filtroInteres);
      const coincideFuente =
        this.filtroFuente === 'Todos' || alerta.fuente === this.filtroFuente;
      const coincideValoracion =
        this.filtroValoracion === 'Todos' ||
        alerta.valoracion === this.filtroValoracion;
      const coincideImpacto = alerta.impactos >= this.filtroImpacto;
      const coincideFechaDesde =
        !this.fechaDesde || alerta.fecha >= this.fechaDesde;
      const coincideFechaHasta =
        !this.fechaHasta || alerta.fecha <= this.fechaHasta;

      return (
        coincideBusqueda &&
        coincideInteres &&
        coincideFuente &&
        coincideValoracion &&
        coincideImpacto &&
        coincideFechaDesde &&
        coincideFechaHasta
      );
    });
  }

  resetFiltros(): void {
    this.filtroBusqueda = '';
    this.filtroInteres = 'Todos';
    this.filtroFuente = 'Todos';
    this.filtroValoracion = 'Todos';
    this.filtroImpacto = 0;
    this.fechaDesde = undefined;
    this.fechaHasta = undefined;
    this.aplicarFiltros();
  }

  obtenerClaseValoracion(valoracion: string): string {
    switch (valoracion) {
      case 'Buena':
        return 'verde';
      case 'Mala':
        return 'rojo';
      default:
        return '';
    }
  }

  abrirEnlace(event: any): void {
    const url = event.target.value;
    if (url) {
      window.open(url, '_blank');
    }
  }
}
