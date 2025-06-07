import { Component, OnInit } from '@angular/core';
import * as d3 from 'd3';
import { combineLatest } from 'rxjs';
import { PlotChartsService } from '../../../core/services/graficas/plot-charts.service';
import { PublicacionesService } from '../../alertas/publicaciones-feed/publicaciones-feed.service';
import { FuenteService } from '../../fuentes/fuentes.service';
import { CommonModule } from '@angular/common';
import { SpinnerComponent } from '../../../core/plantillas/spinner/spinner.component';
import { ConceptosService } from '../../conceptos/conceptos.service';
import { DataTrasnformerService } from '../../../core/services/graficas/data-transformer.service';

@Component({
  selector: 'app-multi-linea',
  imports: [SpinnerComponent, CommonModule],
  templateUrl: './multi-linea.component.html',
  styleUrl: './multi-linea.component.css',
})
export class MultiLineaComponent implements OnInit {
  private datosFuentes: { fecha: Date; serie: string; total: number }[] = [];
   private datosConceptos: { fecha: Date; serie: string; total: number }[] = [];

  // <--- datos para la gráfica
  loading = true; // <--- flag de carga

  constructor(
    private publicacionesService: PublicacionesService,
    private fuentesService: FuenteService,
    private conceptosService: ConceptosService,
    private plotChartsService: PlotChartsService,
    private dataTrasnformerService: DataTrasnformerService
  ) {
    this.fuentesService.getAll();
    this.publicacionesService.getAll();
    this.conceptosService.getAll();
  }

  ngOnInit(): void {
    this.loading = true;
    combineLatest([
      this.fuentesService.items$,
      this.publicacionesService.items$,
    ]).subscribe(([fuentes, noticias]) => {
      this.datosFuentes =
        this.dataTrasnformerService.transformarDatosRelacionadosTiempo(
          noticias,
          fuentes,
          'fuente_id', // campoRelacionId (directo en publicaciones)
          'nombre', // campoNombreEntidad
          'fuente'
        );
      this.dibujarGraficaPublicacionesFuenteTiempo();
    });
    combineLatest([
      this.publicacionesService.items$,
      this.conceptosService.items$,
    ]).subscribe(([publicaciones, conceptos]) => {
      this.datosConceptos =
        this.dataTrasnformerService.transformarDatosRelacionadosTiempo(
          publicaciones,
          conceptos,
          'publicaciones_relacionadas_ids', // campoRelacionId (directo en publicaciones)
          'nombre', // campoNombreEntidad
          'concepto'
        );
      this.dibujarGraficaConceptosFuenteTiempo();
    });
  }

  private dibujarGraficaPublicacionesFuenteTiempo() {
    // uso setTimeout para esperar al next tick de Angular / DOM
    setTimeout(() => {
      this.plotChartsService.createMultiLineChart({
        selector: '#publicacionesFuenteTiempo',
        data: this.datosFuentes,
        width: 800,
        height: 400,
        xField: 'fecha',
        yField: 'total',
        seriesField: 'serie',
        title: 'Noticias por fuente a lo largo del tiempo',
        xAxisLabel: 'Fecha',
        yAxisLabel: 'Noticias',
        legend: true,
      });
      this.loading = false; // oculto la máscara
    }, 1000);
  }

  private dibujarGraficaConceptosFuenteTiempo() {
    // uso setTimeout para esperar al next tick de Angular / DOM
    setTimeout(() => {
      this.plotChartsService.createMultiLineChart({
        selector: '#conceptosFuenteTiempo',
        data: this.datosConceptos,
        width: 800,
        height: 400,
        xField: 'fecha',
        yField: 'total',
        seriesField: 'serie',
        title: 'Conceptos publicados a lo largo del tiempo',
        xAxisLabel: 'Fecha',
        yAxisLabel: 'Noticias',
        legend: true,
      });
      this.loading = false; // oculto la máscara
    }, 1000);
  }
}
