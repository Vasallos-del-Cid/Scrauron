import { Component, OnInit } from '@angular/core';
import * as d3 from 'd3';
import { combineLatest } from 'rxjs';
import { PlotChartsService } from '../../../core/services/graficas/plot-charts.service';
import { PublicacionesService } from '../../alertas/publicaciones-feed/publicaciones-feed.service';
import { FuenteService } from '../../fuentes/fuentes.service';
import { MultiLineaChartService } from './multi-linea-chart.service';
import { CommonModule } from '@angular/common';
import { SpinnerComponent } from '../../../core/plantillas/spinner/spinner.component';

@Component({
  selector: 'app-multi-linea',
  imports: [SpinnerComponent,CommonModule],
  templateUrl: './multi-linea.component.html',
  styleUrl: './multi-linea.component.css',
})
export class MultiLineaComponent implements OnInit {
  
  private datos: { fecha: Date; fuente: string; total: number }[] = [];
  
  // <--- datos para la gráfica
  loading = true;  // <--- flag de carga

  constructor(
    private publicacionesService: PublicacionesService,
    private fuentesService: FuenteService,
    private plotChartsService: PlotChartsService,
    private multiLineaChartService: MultiLineaChartService
  ) {
    this.fuentesService.getAll();
    this.publicacionesService.getAll();
  }

  ngOnInit(): void {
    this.loading = true; 
    combineLatest([
      this.fuentesService.items$,
      this.publicacionesService.items$,
    ]).subscribe(([fuentes, noticias]) => {
      this.datos =
        this.multiLineaChartService.transformarDatosPublicacionesPorFuente(
          noticias,
          fuentes
        );
      this.dibujarGrafica();
    });
  }

  private dibujarGrafica() {
    // uso setTimeout para esperar al next tick de Angular / DOM
    setTimeout(() => {
    this.plotChartsService.createMultiLineChart({
      selector: '#multiChart',
      data: this.datos,
      width: 800,
      height: 400,
      xField: 'fecha',
      yField: 'total',
      seriesField: 'fuente',
      title: 'Noticias por fuente a lo largo del tiempo',
      xAxisLabel: 'Fecha',
      yAxisLabel: 'Noticias',
      legend: true,
    });
      this.loading = false;                         // oculto la máscara
    }, 1000);
  }
}
