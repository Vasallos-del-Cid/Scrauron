import { AfterViewInit, Component, OnInit } from '@angular/core';
import { D3ChartService } from '../../../core/services/graficas/d3-charts.service';
import { ConceptosService } from '../../conceptos/conceptos.service';
import { PlotChartsService } from '../../../core/services/graficas/plot-charts.service';
import { CommonModule } from '@angular/common';
import { SpinnerComponent } from '../../../core/plantillas/spinner/spinner.component';

@Component({
  selector: 'app-bar-chart',
  imports: [SpinnerComponent, CommonModule],
  template: `<div class="chart-container">
    <div id="barChartContainer">
      <app-spinner *ngIf="loading" message="Cargando gráfico..."></app-spinner>
    </div>
  </div>`,
  styleUrl: './bar-chart.component.css',
})
export class BarChartComponent implements AfterViewInit, OnInit {
  loading = true; // <--- flag de carga
  private data: any[] = [];
  private isViewInitialized = false;

  constructor(
    private graficaService: PlotChartsService,
    private conceptosService: ConceptosService
  ) {
    conceptosService.getAll();
  }

  ngOnInit(): void {
    this.conceptosService.items$.subscribe((conceptos) => {
      this.data = conceptos.map((concepto) => ({
        label: concepto.nombre,
        value: concepto.publicaciones_relacionadas_ids?.length || 0, // Asegúrate de que num_menciones esté definido
      }));
      if (this.isViewInitialized) {
        this.dibujarGrafica();
      }
    });
  }

  ngAfterViewInit() {
    this.isViewInitialized = true;
    if (this.data.length > 0) {
      this.dibujarGrafica();
    }
  }

  private dibujarGrafica() {
    setTimeout(() => {
      this.graficaService.createBarChart({
        selector: '#barChartContainer',
        data: this.data,
        width: 600,
        height: 400,
        xField: 'label',
        yField: 'value',
        barColor: '#4062b9', // Color verde para las barras
        xAxisLabel: 'Conceptos de interés',
        yAxisLabel: 'Número de publicaciones',
        title: 'Total de publicaciones por concepto',
        fontSize: 14,
        fontFamily: 'Arial',
      });

      this.loading = false; // oculto la máscara
    }, 500);
  }
}
