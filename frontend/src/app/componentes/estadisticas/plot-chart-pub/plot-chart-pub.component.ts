import { Component, ElementRef, Input, OnChanges, ViewChild, Renderer2 } from '@angular/core';
import * as d3 from 'd3';

@Component({
  selector: 'app-grafico-barras',
  templateUrl: './plot-chart-pub.component.html',
  styleUrls: ['./plot-chart-pub.component.css']
})
export class GraficoBarrasComponent implements OnChanges {
  @Input() datosGrafico: { datoX: string; datoY: number; conteo?: number }[] = [];
  @Input() tituloGrafico: string = "";
  @Input() ejeX: string = "";
  @Input() ejeY: string = "";

  @ViewChild('grafico') private graficoContainer!: ElementRef;
  mostrarTodos: boolean = false;
  esFecha: boolean = false;
  datosVisibles: { datoX: string; datoY: number; conteo?: number }[] = [];

  constructor(private renderer: Renderer2) {}

  ngOnChanges(): void {
    if (this.datosGrafico && this.graficoContainer) {
      this.mostrarTodos = false;
      this.prepararDatos();
      this.crearGrafico(this.datosVisibles);
    }
  }

  prepararDatos(): void {
  const fechaRegex = /^\d{4}-\d{2}-\d{2}$/;
  this.esFecha = fechaRegex.test(this.datosGrafico[0]?.datoX);

  const datosOrdenados = [...this.datosGrafico].sort((a, b) => {
    if (this.esFecha) {
      return new Date(b.datoX).getTime() - new Date(a.datoX).getTime(); // Más recientes primero
    }
    return b.datoY - a.datoY; // Mayores valores primero
  });

  const topDatos = datosOrdenados.slice(0, 20);
  this.datosVisibles = this.esFecha ? topDatos.reverse() : topDatos;
}



  crearGrafico(datos: { datoX: string; datoY: number; conteo?: number }[], container: ElementRef = this.graficoContainer, anchoExtra: boolean = false, mostrarBoton: boolean = true): void {
    const element = container.nativeElement;
    d3.select(element).selectAll('*').remove();

    const margin = { top: 50, right: 40, bottom: 100, left: 40 };
    const baseWidth = 700;
    const width = (anchoExtra ? element.clientWidth : baseWidth) - margin.left - margin.right;
    const height = 350 - margin.top - margin.bottom;

    const svgBase = d3.select(element)
      .append('svg')
      .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .style('width', '100%')
      .style('height', '95%');

    const svg = svgBase.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -10)
      .attr("text-anchor", "middle")
      .style("font-size", "22px")
      .style("font-weight", "bold")
      .style("fill", "#003366")
      .text(this.tituloGrafico);

    const x = d3.scaleBand()
      .domain(datos.map(d => d.datoX))
      .range([0, width])
      .padding(0.1);

    let yMax: number;
    if (this.tituloGrafico.includes('Tono')) {
      yMax = 10;
    } else {
      const maxY = d3.max(datos, d => d.datoY)!;
      yMax = maxY + maxY * 0.2;
    }

    const y = d3.scaleLinear()
      .domain([0, yMax])
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
    const doc = container.nativeElement.ownerDocument;
    const tooltip = d3.select(doc.body)
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
      .style("z-index", "9999");

    svg.selectAll('.bar')
      .data(datos)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.datoX)!)
      .attr('y', d => y(d.datoY))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.datoY))
      .attr('fill', 'steelblue')
      .on('mouseover', (event, d) => {
        const valorRedondeado = Number(d.datoY.toFixed(2));
        const valorMostrado = valorRedondeado % 1 === 0 ? valorRedondeado.toFixed(0) : valorRedondeado.toFixed(2);
        tooltip
          .style('display', 'block')
          .html(`${this.ejeX}: ${d.datoX}<br>${this.ejeY}: ${valorMostrado}${d.conteo !== undefined ? `<br>Publicaciones: ${d.conteo}` : ''}`);
      })
      .on('mousemove', (event) => {
        tooltip
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY + 10) + 'px');
      })
      .on('mouseout', () => {
        tooltip.style('display', 'none');
      });

    if (mostrarBoton && !this.mostrarTodos && this.datosGrafico.length > 20) {
      const button = this.renderer.createElement('button');
      const text = this.renderer.createText('Ver todos');
      this.renderer.appendChild(button, text);
      this.renderer.setStyle(button, 'position', 'absolute');
      this.renderer.setStyle(button, 'top', '10px');
      this.renderer.setStyle(button, 'right', '10px');
      this.renderer.setStyle(button, 'z-index', '1000');
      this.renderer.setStyle(button, 'background-color', '#23333c');
      this.renderer.setStyle(button, 'color', 'white');
      this.renderer.setStyle(button, 'padding', '8px 12px');
      this.renderer.setStyle(button, 'border', 'none');
      this.renderer.setStyle(button, 'border-radius', '4px');
      this.renderer.setStyle(button, 'cursor', 'pointer');
      this.renderer.listen(button, 'click', () => this.abrirVentanaEmergente());
      this.renderer.appendChild(element, button);
    }
  }

  abrirVentanaEmergente(): void {
    const fechaRegex = /^\d{4}-\d{2}-\d{2}$/;
    const esFecha = fechaRegex.test(this.datosGrafico[0]?.datoX);

    const datosOrdenados = [...this.datosGrafico].sort((a, b) => {
      if (esFecha) {
        return new Date(a.datoX).getTime() - new Date(b.datoX).getTime();
      }
      return b.datoY - a.datoY;
    });

    const popup = window.open('', '_blank', 'width=1400,height=700,scrollbars=yes,resizable=yes');
    if (popup) {
      popup.document.write('<html><head><title>Todos los datos</title><style>body{margin:0;padding:0;}#grafico-full{width:100vw;height:100vh;}</style></head><body><div id="grafico-full"></div></body></html>');
      popup.document.close();

      const container = popup.document.getElementById('grafico-full');
      if (container) {
        const wrapper = this.renderer.createElement('div');
        this.renderer.setStyle(wrapper, 'width', '100%');
        this.renderer.setStyle(wrapper, 'height', '100%');
        this.renderer.appendChild(container, wrapper);

        const hostRef = new ElementRef(wrapper);
        this.crearGrafico(datosOrdenados, hostRef, true, false);

        popup.addEventListener('resize', () => {
          d3.select(wrapper).selectAll('*').remove();
          this.crearGrafico(datosOrdenados, hostRef, true, false);
        });
      }
    }
  }

  verTodos(): void {
    this.abrirVentanaEmergente();
  }
}