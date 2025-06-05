import { Injectable } from '@angular/core';
import * as d3 from 'd3';
import { ChartConfig } from './chart-config.model';

@Injectable({
  providedIn: 'root'
})
export class D3ChartService {

  constructor() {}

  createBarChart(config: ChartConfig): void {
    const margin = config.margin || { top: 20, right: 30, bottom: 40, left: 40 };
    const width = config.width - margin.left - margin.right;
    const height = config.height - margin.top - margin.bottom;

    const svg = d3.select(config.selector)
      .append('svg')
      .attr('width', config.width)
      .attr('height', config.height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
      .domain(config.data.map(d => d.label))
      .range([0, width])
      .padding(0.1);

    const y = d3.scaleLinear()
      .domain([0, d3.max(config.data, d => d.value)])
      .range([height, 0]);

    svg.append('g')
      .call(d3.axisLeft(y));

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    svg.selectAll('.bar')
      .data(config.data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.label) ?? 0)
      .attr('y', d => y(d.value))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.value))
      .attr('fill', config['barColor'] || 'steelblue');
  }

  // Otros tipos de gráficos pueden seguir la misma estructura
}