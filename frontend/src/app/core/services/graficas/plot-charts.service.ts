// === plot-chart.service.ts ===
import { Injectable } from '@angular/core';
import * as Plot from '@observablehq/plot';
import { ChartConfig } from './chart-config.model';

@Injectable({
  providedIn: 'root',
})
export class PlotChartsService {
  createBarChart(config: ChartConfig): void {
    const chart = Plot.plot({
      marks: [
        Plot.barY(config.data, {
          x: config.xField,
          y: config.yField,
          fill: config.barColor,
        }),
      ],
      width: config.width,
      height: config.height,
      marginLeft: config.margin?.left ?? 50,
      marginBottom: config.margin?.bottom ?? 50,
      x: { label: config.xAxisLabel || config.xField },
      y: { label: config.yAxisLabel || config.yField },
      style: {
        background: config.backgroundColor || 'white',
        fontSize: config.fontSize ? `${config.fontSize}px` : undefined,
        fontFamily: config.fontFamily || undefined,
      },
    });
    this.renderChart(config.selector, chart, config.title);
  }

  createLineChart(config: ChartConfig): void {
    const chart = Plot.plot({
      marks: [
        Plot.lineY(config.data, {
          x: config.xField,
          y: config.yField,
          stroke: config.lineColor,
        }),
      ],
      width: config.width,
      height: config.height,
      marginLeft: config.margin?.left ?? 50,
      marginBottom: config.margin?.bottom ?? 50,
      x: { label: config.xAxisLabel || config.xField },
      y: { label: config.yAxisLabel || config.yField },
      style: {
        background: config.backgroundColor || 'white',
        fontSize: config.fontSize ? `${config.fontSize}px` : undefined,
        fontFamily: config.fontFamily || undefined,
      },
    });
    this.renderChart(config.selector, chart, config.title);
  }

  private renderChart(
    selector: string,
    chartElement: Element,
    title?: string
  ): void {
    const container = document.querySelector(selector);
    if (container) {
      container.innerHTML = '';

      const wrapper = document.createElement('div');
      wrapper.style.display = 'inline-block';
      wrapper.style.textAlign = 'center';

      if (title) {
        const titleElement = document.createElement('h3');
        titleElement.textContent = title;
        titleElement.style.marginBottom = '8px';
        wrapper.appendChild(titleElement);
      }

      wrapper.appendChild(chartElement);
      container.appendChild(wrapper);
    }
  }
}
