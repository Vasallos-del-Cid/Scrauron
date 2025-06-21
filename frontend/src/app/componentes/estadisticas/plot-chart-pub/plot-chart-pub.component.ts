import { Component, ElementRef, Input, OnChanges, ViewChild } from '@angular/core';
import * as d3 from 'd3';

@Component({
  selector: 'app-grafico-barras',
  templateUrl: './plot-chart-pub.component.html',
  styleUrls: ['./plot-chart-pub.component.css']
})
export class GraficoBarrasComponent implements OnChanges {
  @Input() datosGrafico: { datoX: string; datoY: number }[] = [];
  @Input() tituloGrafico: string = "";
  @Input() ejeX: string = "";
  @Input() ejeY: string = "";

  @ViewChild('grafico') private graficoContainer!: ElementRef;

  ngOnChanges(): void {
    if (this.datosGrafico && this.graficoContainer) {
      this.crearGrafico();
    }
  }

  private crearGrafico(): void {
    const element = this.graficoContainer.nativeElement;
    d3.select(element).selectAll('*').remove();

    const margin = { top: 50, right: 40, bottom: 100, left: 40 };
    const width = 700 - margin.left - margin.right;
    const height = 350 - margin.top - margin.bottom;

    const self = this;

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
      .style("fill", "#003366") // Aplica el color azul
      .text(this.tituloGrafico);


    const x = d3.scaleBand()
      .domain(this.datosGrafico.map(d => d.datoX))
      .range([0, width])
      .padding(0.1);

    const y = d3.scaleLinear()
      .domain([0, d3.max(this.datosGrafico, d => d.datoY)!])
      .nice()
      .range([height, 0]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end')
      .style('font-size', '170%');

    svg.append('g')
      .call(d3.axisLeft(y))
      .selectAll('text')
      .style('font-size', '150%');

    // Crear tooltip
    const tooltip = d3.select('body')
      .append("div")
      .attr("class", "tooltip")
      .style("position", "absolute")
      .style("background", "#fff")
      .style("padding", "8px")
      .style("border", "1px solid #ccc")
      .style("border-radius", "4px")
      .style("pointer-events", "none")
      .style("font-size", "14px")
      .style("display", "none")
      .style("z-index", "9999"); // Muy importante para que quede por encima

    svg.selectAll('.bar')
      .data(this.datosGrafico)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.datoX)!)
      .attr('y', d => y(d.datoY))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.datoY))
      .attr('fill', 'steelblue')
      .on('mouseover', (event, d) => {
        tooltip
          .style('display', 'block')
          .html(`${this.ejeX}: ${d.datoX}<br>${this.ejeY}: ${d.datoY}`);
      })
      .on('mousemove', (event) => {
        tooltip
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY + 10) + 'px');
      })
      .on('mouseout', () => {
        tooltip.style('display', 'none');
      });


  }
}
