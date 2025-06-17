import { Component, ElementRef, Input, OnChanges, ViewChild } from '@angular/core';
import * as d3 from 'd3';

@Component({
  selector: 'app-grafico-barras',
  templateUrl: './plot-chart-pub.component.html',
  styleUrls: ['./plot-chart-pub.component.css']
})
export class GraficoBarrasComponent implements OnChanges {
  @Input() datosPublicacionesDia: { fecha: string; publicaciones: number }[] = [];
  @ViewChild('grafico') private graficoContainer!: ElementRef;

  ngOnChanges(): void {
    if (this.datosPublicacionesDia && this.graficoContainer) {
      this.crearGrafico();
    }
  }

  private crearGrafico(): void {
    const element = this.graficoContainer.nativeElement;
    d3.select(element).selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 50, left: 50 };
    const width = 800 - margin.left - margin.right;
    const height = 350 - margin.top - margin.bottom;

    const svgBase = d3.select(element)
      .append('svg')
      .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .style('width', '100%')
      .style('height', '100%');

    const svg = svgBase.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -10)
      .attr("text-anchor", "middle")
      .style("font-size", "22px")
      .style("font-weight", "bold")
      .text("Publicaciones por día");

    const x = d3.scaleBand()
      .domain(this.datosPublicacionesDia.map(d => d.fecha))
      .range([0, width])
      .padding(0.1);

    const y = d3.scaleLinear()
      .domain([0, d3.max(this.datosPublicacionesDia, d => d.publicaciones)!])
      .nice()
      .range([height, 0]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end')
      .style('font-size', '20px'); // ⬅️ Tamaño de texto del eje X

    svg.append('g')
      .call(d3.axisLeft(y))
      .selectAll('text')
      .style('font-size', '20px'); // ⬅️ Tamaño de texto del eje Y


    svg.selectAll('.bar')
      .data(this.datosPublicacionesDia)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.fecha)!)
      .attr('y', d => y(d.publicaciones))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.publicaciones))
      .attr('fill', 'steelblue');
  }
}
