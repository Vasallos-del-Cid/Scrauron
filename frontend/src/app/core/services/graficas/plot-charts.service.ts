// === plot-chart.service.ts ===
import { Injectable } from '@angular/core';
import * as Plot from '@observablehq/plot';
import * as d3 from 'd3';
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
      y: {
        label: config.yAxisLabel || config.yField,
        grid: true,
        // si config.yDomain está definido lo usamos, si no auto        domain: config.yDomain ?? d3.extent(config.data, d => d[config.yField!]) as [number, number]
      },
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

  createMultiLineChart(config: ChartConfig): void {
    const seriesField = config['seriesField'] || 'serie';

    const chart = Plot.plot({
      width: config.width,
      height: config.height,
      marginLeft: config.margin?.left ?? 50,
      marginBottom: config.margin?.bottom ?? 50,
      x: {
        type: 'time',
        label: config.xAxisLabel || config.xField,
        domain: d3.extent(config.data, (d) => d[config.xField!]) as [
          Date,
          Date
        ],
      },
      y: {
        label: config.yAxisLabel || config.yField,
        grid: true,
      },
      color: {
        legend: config.legend !== false,
        type: 'categorical',
        range: d3.schemeTableau10.concat(d3.schemeSet3).flat(),
      },
      style: {
        background: config.backgroundColor || 'white',
        fontSize: config.fontSize ? `${config.fontSize}px` : undefined,
        fontFamily: config.fontFamily || undefined,
      },
      marks: [
        Plot.ruleY([0]),
        Plot.lineY(config.data, {
          x: config.xField,
          y: config.yField,
          stroke: seriesField,
          strokeOpacity: 0.6,
          strokeWidth: 2,
          tip: true,
        }),
        Plot.dot(config.data, {
          x: config.xField,
          y: config.yField,
          stroke: seriesField,
          fill: seriesField,
          tip: true,
        }),
      ],
    });

    this.renderChart(config.selector, chart, config.title);

    // Interactividad: resaltar serie al hacer clic
    setTimeout(() => {
      const container = document.querySelector(config.selector);
      if (container) {
        const targets = container.querySelectorAll(
          'path[stroke], circle[stroke]'
        );
        targets.forEach((el: Element) => {
          el.addEventListener('click', (ev) => {
            ev.stopPropagation();
            const color = el.getAttribute('stroke');
            targets.forEach((e: Element) => {
              const match = e.getAttribute('stroke') === color;
              e.setAttribute('opacity', match ? '1' : '0.5');
              e.setAttribute('stroke-width', match ? '3' : '1');
            });
          });
        });
        container.addEventListener('click', () => {
          targets.forEach((e) => {
            e.setAttribute('opacity', '1');
            e.setAttribute('stroke-width', '2');
          });
        });
      }
    }, 0);
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
