import { Component, OnInit, Input, OnChanges, SimpleChanges } from '@angular/core';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';
import { FeatureCollection, Geometry, GeoJsonProperties } from 'geojson';
import { Topology } from 'topojson-specification';
import { CommonModule } from '@angular/common';
import { PAISES_EQUIVALENTES } from '../../../environments/paises-equivalentes';

@Component({
    selector: 'app-mapa-mundial',
    standalone: true,
    imports: [CommonModule],
    template: `
    <h2 style="text-align: center; margin-top: 5px; margin-bottom: 5px; font-size: clamp(0.7rem, 1vw, 1rem); color: #003366;">
  Número de publicaciones por país en el que suceden
    </h2>
  <div id="mapa-d3" style="display: flex; justify-content: center; border: 1px solid rgb(102, 138, 173); border-radius: 8px; padding: 10px; background-color: #f9f9f9;  box-sizing: border-box;
  margin: 0 auto; max-width: 960px"></div>


  <div style="display: flex; justify-content: space-between; margin-top: 2%; flex-wrap: wrap; gap: 10px; max-width: 100%; box-sizing: border-box;">
    <div style="flex: 0 0 25%; min-width: 100px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.2); padding: 2%; border-radius: 8px; text-align: center; font-size: clamp(0.5rem, 1vw, 0.8rem);">
      <div style="color: #003366; font-weight: bold; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" [title]="'Total publicaciones:'">Total publicaciones:</div>
      <div>{{ totalPublicaciones }}</div>
    </div>
    <div style="flex: 0 0 30%; min-width: 100px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.2); padding: 2%; border-radius: 8px; text-align: center; font-size: clamp(0.5rem, 1vw, 0.8rem);">
      <div style="color: #003366; font-weight: bold; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" [title]="'País con más publicaciones:'">País con más publicaciones:</div>
      <div>{{ nombrePaisConMasPublicaciones }}</div>
    </div>
    <div style="flex: 0 0 25%; min-width: 100px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.2); padding: 2%; border-radius: 8px; text-align: center; font-size: clamp(0.7rem, 1vw, 0.8rem);">
      <div style="color: #003366; font-weight: bold; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" [title]="'Tono medio:'">Tono medio:</div>
      <div>{{ tonoMedioGeneral | number:'1.1-2' }}</div>
    </div>
  </div>
  `
})
export class MapaMundialComponent implements OnInit, OnChanges {
    @Input() dataPorPais: Record<string, number> = {};
    @Input() paisConMasPublicaciones: string | null = null;
    @Input() tonoMedioGeneral: number = 0;
    @Input() totalPublicaciones: number = 0;

    nombrePaisConMasPublicaciones: string = '';
    private iso3ANombre: Record<string, string> = {};
    private nombreInglesAIso3: Record<string, string> = {};

    ngOnInit(): void {
        for (const pais of PAISES_EQUIVALENTES) {
            this.iso3ANombre[pais.iso3] = pais.espanol;
            this.nombreInglesAIso3[pais.ingles] = pais.iso3;
        }
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['dataPorPais']) {
            this.dibujarMapa();
        }
        if (changes['paisConMasPublicaciones']) {
            this.nombrePaisConMasPublicaciones = this.paisConMasPublicaciones
                ? (PAISES_EQUIVALENTES.find(p => p.iso3 === this.paisConMasPublicaciones)?.espanol || this.paisConMasPublicaciones)
                : '';
        }
    }

    public dibujarMapa(): void {
        const tooltip = d3.select("#mapa-d3")
            .append("div")
            .style("position", "absolute")
            .style("background", "#fff")
            .style("padding", "2px 10px")
            .style("border", "1px solid #ccc")
            .style("border-radius", "5px")
            .style("pointer-events", "none")
            .style("display", "none")
            .style("font-size", "14px")
            .style("z-index", "10");

        d3.select("#mapa-d3 svg").remove();

        const svg = d3.select("#mapa-d3").append("svg")
            .attr("viewBox", "0 0 960 600")
            .attr("preserveAspectRatio", "xMidYMid meet")
            .style("width", "100%")
            .style("height", "100%")
            .style("margin-top", "1%");

        const g = svg.append("g");

        const projection = d3.geoNaturalEarth1()
            .scale(210)
            .translate([460, 260]);

        const path = d3.geoPath(projection);

        const maxValor = Math.max(...Object.values(this.dataPorPais), 1);
        const color = d3.scaleLinear<string>()
            .domain([1, maxValor])
            .range(["#cce5ff", "#003366"]);

        // Zoom global
        const zoom = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([1, 8])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });

        svg.call(zoom);

        // Cargar mapa y dibujar países
        d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then((worldData) => {
            const world = worldData as Topology;
            const featureCollection = topojson.feature(
                world,
                world.objects['countries']
            ) as unknown as FeatureCollection<Geometry, GeoJsonProperties>;

            g.selectAll("path")
                .data(featureCollection.features)
                .join("path")
                .attr("d", path)
                .attr("fill", (d: any) => {
                    const nombre = d.properties.name;
                    const iso3 = this.nombreInglesAIso3[nombre];
                    const val = iso3 ? this.dataPorPais[iso3] : undefined;
                    return val != null ? color(val) : "#ccc";
                })
                .attr("stroke", "#444")          // Gris oscuro
                .attr("stroke-width", 0.2)       // Línea fina

                .on("mouseover", (event, d: any) => {
                    const nombre = d.properties.name;
                    const iso3 = this.nombreInglesAIso3[nombre];
                    const nombreMostrado = iso3 ? this.iso3ANombre[iso3] : 'Desconocido';
                    const valor = iso3 ? this.dataPorPais[iso3] ?? "Sin datos" : "Sin datos";
                    tooltip.style("display", "block").html(`${nombreMostrado}: ${valor}`);
                })
                .on("mousemove", (event) => {
                    tooltip.style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 180) + "px");
                })
                .on("mouseout", () => {
                    tooltip.style("display", "none");
                })
                .on("dblclick", (event, d: any) => {
                    const [[x0, y0], [x1, y1]] = path.bounds(d);
                    const dx = x1 - x0;
                    const dy = y1 - y0;
                    const x = (x0 + x1) / 2;
                    const y = (y0 + y1) / 2;
                    const scale = Math.max(1, Math.min(8, 0.9 / Math.max(dx / 960, dy / 500)));
                    const translate = [480 - scale * x, 250 - scale * y];

                    svg.transition()
                        .duration(750)
                        .call(
                            zoom.transform,
                            d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
                        );
                });
        });
    }


}
