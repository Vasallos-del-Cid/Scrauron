import { Component, ElementRef, Input, OnChanges, ViewChild } from '@angular/core';
import * as d3 from 'd3';

@Component({
  selector: 'app-grafico-barras',
  templateUrl: './plot-chart-pub.component.html',
  styleUrls: ['./plot-chart-pub.component.css']
})

// Recibe una lista de datos con pares string y number, un titulo del grafico, y el nombre de los ejes
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

    const margin = { top: 30, right: 30, bottom: 100, left: 50 };
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
      .style('font-size', '20px'); // ⬅️ Tamaño de texto del eje X

    svg.append('g')
      .call(d3.axisLeft(y))
      .selectAll('text')
      .style('font-size', '20px'); // ⬅️ Tamaño de texto del eje Y


    svg.selectAll('.bar')
      .data(this.datosGrafico)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.datoX)!)
      .attr('y', d => y(d.datoY))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.datoY))
      .attr('fill', 'steelblue');
  }
}
