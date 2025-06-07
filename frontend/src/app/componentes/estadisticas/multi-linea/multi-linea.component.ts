import { Component, OnInit } from '@angular/core';
import * as d3 from 'd3';
import { combineLatest } from 'rxjs';
import { PlotChartsService } from '../../../core/services/graficas/plot-charts.service';
import { PublicacionesService } from '../../alertas/publicaciones-feed/publicaciones-feed.service';
import { FuenteService } from '../../fuentes/fuentes.service';
import { MultiLineaChartService } from './multi-linea-chart.service';

@Component({
  selector: 'app-multi-linea',
  imports: [],
  templateUrl: './multi-linea.component.html',
  styleUrl: './multi-linea.component.css',
})
export class MultiLineaComponent implements OnInit {
  private fuentes: any[] = [];
  private noticias: any[] = [];
  private datos: { fecha: Date; fuente: string; total: number }[] = [];
  private isViewInitialized = false;

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
  }
}
