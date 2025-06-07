import { Injectable } from '@angular/core';
import * as d3 from 'd3';
import { PublicacionesService } from '../../alertas/publicaciones-feed/publicaciones-feed.service';
import { FuenteService } from '../../fuentes/fuentes.service';

@Injectable({
  providedIn: 'root'
})
export class MultiLineaChartService {

  constructor() {}

  transformarDatosPublicacionesPorFuente(publicaciones: any[], fuentes: any[]): { fecha: Date, fuente: string, total: number }[] {
    const fuenteMap = new Map(fuentes.map(f => [f._id, f.nombre]));

    const agregadas = d3.rollups(
      publicaciones,
      v => v.length,
      d => d3.timeFormat('%Y-%m-%d')(new Date(d.fecha)),
      d => fuenteMap.get(d.fuente_id) || d.fuente_id
    );

    const resultado: { fecha: Date, fuente: string, total: number }[] = [];
    agregadas.forEach(([fecha, fuentesInternas]) => {
      fuentesInternas.forEach(([fuente, total]) => {
        resultado.push({
          fecha: new Date(fecha),
          fuente,
          total
        });
      });
    });

    return resultado;
  }
}
