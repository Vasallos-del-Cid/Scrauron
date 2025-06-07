import { Component, AfterViewInit } from '@angular/core';
import { PlotChartsService } from '../../../core/services/graficas/plot-charts.service';


@Component({
  selector: 'app-dashboard',
  template: `
    <div class="dashboard">
      <h2>Evolución de Ventas</h2>
      <div id="lineChart"></div>
    </div>
  `,
  styles: [`
    .dashboard {
      padding: 20px;
    }
    #lineChart {
      margin-top: 20px;
    }
  `]
})
export class PlotChartComponent implements AfterViewInit {

  constructor(private plotChartService: PlotChartsService) {}

  ngAfterViewInit(): void {
    const sampleData = [
      { fecha: '2024-01-01', valor: 100 },
      { fecha: '2024-01-02', valor: 120 },
      { fecha: '2024-01-03', valor: 90 },
      { fecha: '2024-01-04', valor: 150 },
      { fecha: '2024-01-05', valor: 130 }
    ];

/*     this.plotChartService.createLineChart('#lineChart', sampleData, 'fecha', 'valor'); */
  }
}
