import { AfterViewInit, Component } from '@angular/core';
import { D3ChartService } from '../../../core/services/graficas/d3-charts.service';

@Component({
  selector: 'app-bar-chart',
  imports: [],
  template: `<div id="barChartContainer"></div>`,
  styleUrl: './bar-chart.component.css',
})
export class BarChartComponent implements AfterViewInit {
  constructor(private d3Service: D3ChartService) {}

  ngAfterViewInit() {
    this.d3Service.createBarChart({
      selector: '#barChartContainer',
      width: 600,
      height: 400,
      data: [
        { label: 'A', value: 30 },
        { label: 'B', value: 80 },
        { label: 'C', value: 45 },
      ],
      barColor: '#ff6600',
    });
  }
}
