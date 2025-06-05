// === plot-chart.service.ts ===
import { Injectable } from '@angular/core';
import * as Plot from '@observablehq/plot';

@Injectable({
  providedIn: 'root'
})
export class PlotChartsService {

  createBarChart(containerSelector: string, data: any[], xField: string, yField: string): void {
    const chart = Plot.plot({
      marks: [Plot.barY(data, { x: xField, y: yField })],
      width: 600,
      height: 400,
      marginLeft: 50,
      marginBottom: 50,
      x: { label: xField },
      y: { label: yField }
    });
    this.renderChart(containerSelector, chart);
  }

  createLineChart(containerSelector: string, data: any[], xField: string, yField: string): void {
    const chart = Plot.plot({
      marks: [Plot.lineY(data, { x: xField, y: yField })],
      width: 600,
      height: 400,
      marginLeft: 50,
      marginBottom: 50,
      x: { label: xField },
      y: { label: yField }
    });
    this.renderChart(containerSelector, chart);
  }

  private renderChart(selector: string, chartElement: SVGSVGElement | HTMLElement): void {
    const container = document.querySelector(selector);
    if (container) {
      container.innerHTML = '';
      container.appendChild(chartElement);
    }
  }
}
