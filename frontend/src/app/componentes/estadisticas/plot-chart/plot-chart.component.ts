import { Component, AfterViewInit, OnInit } from '@angular/core';
import { PlotChartsService } from '../../../core/services/graficas/plot-charts.service';
import { PublicacionesService } from '../../alertas/publicaciones-feed/publicaciones-feed.service';
import { combineLatest } from 'rxjs';
import { DataTrasnformerService } from '../../../core/services/graficas/data-transformer.service';
import { ConceptosService } from '../../conceptos/conceptos.service';
import { CommonModule } from '@angular/common';
import { mean } from 'd3';
import { SpinnerComponent } from '../../../core/plantillas/spinner/spinner.component';


@Component({
  selector: 'app-dashboard',
  templateUrl: './plot-chart.component.html',
  imports: [SpinnerComponent, CommonModule],
  styles: []
})
export class PlotChartComponent  implements OnInit {
  
   private datosConceptosTono: { fecha: Date; serie: string; valor: number }[] = [];

  // <--- datos para la gráfica
  loading = true; // <--- flag de carga

  constructor(
    private publicacionesService: PublicacionesService,
    private conceptosService: ConceptosService,
    private plotChartsService: PlotChartsService,
    private dataTrasnformerService: DataTrasnformerService
  ) {
    this.publicacionesService.getAll();
    this.conceptosService.getAll();
  }

  ngOnInit(): void {
    combineLatest([
      this.publicacionesService.items$,
      this.conceptosService.items$,
    ]).subscribe(([publicaciones, conceptos]) => {
      this.datosConceptosTono =
        this.dataTrasnformerService.transformarPorEntidad(
          publicaciones,
          conceptos,
          'publicaciones_relacionadas_ids', // campoRelacionId (directo en publicaciones)
          'nombre', // campoNombreEntidad
          items => mean(items, d => d.tono ?? 0) as number
        );
      this.dibujarGraficaConceptosTonoTiempo();
    });
  }


  private dibujarGraficaConceptosTonoTiempo() {
    // uso setTimeout para esperar al next tick de Angular / DOM
    setTimeout(() => {
      this.plotChartsService.createMultiLineChart({
        selector: '#conceptosTonoTiempo',
        data: this.datosConceptosTono,
        width: 800,
        height: 400,
        xField: 'fecha',
        yField: 'valor',
        seriesField: 'serie',
        title: 'Evolución del tono medio de los conceptos de interés',
        xAxisLabel: 'Fecha',
        yAxisLabel: 'Tono medio (1–10)',
        legend: true,
        yDomain: [1, 10]
      });
      this.loading = false; // oculto la máscara
    }, 1000);
  }
}
