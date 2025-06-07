import { Injectable } from '@angular/core';
import * as d3 from 'd3';
import { PublicacionesService } from '../../alertas/publicaciones-feed/publicaciones-feed.service';
import { FuenteService } from '../../fuentes/fuentes.service';

@Injectable({
  providedIn: 'root',
})
export class MultiLineaChartService {
  constructor() {}

  transformarDatosRelacionadosTiempo(
    entidadPrimera: any[],
    entidadSegunda: any[],
    campoRelacionId: string,
    campoNombreEntidad: string,
    etiquetaSerie: string
  ): { fecha: Date; serie: string; total: number }[] {
    const entidadMap = new Map(
      entidadSegunda.map((e) => [e._id, e[campoNombreEntidad]])
    );

    let entidadesConectadas: { fecha: string; serie: string }[] = [];

    if (campoRelacionId === 'fuente_id') {
      entidadesConectadas = entidadPrimera.map((pub) => ({
        fecha: d3.timeFormat('%Y-%m-%d')(new Date(pub.fecha)),
        serie: entidadMap.get(pub.fuente_id) || pub.fuente_id,
      }));
    } else {
      // por ejemplo, conceptos
      entidadSegunda.forEach((entidad) => {
        entidad[campoRelacionId]?.forEach((pubId: string) => {
          const pub = entidadPrimera.find((p) => p._id === pubId);
          if (pub) {
            entidadesConectadas.push({
              fecha: d3.timeFormat('%Y-%m-%d')(new Date(pub.fecha)),
              serie: entidad[campoNombreEntidad],
            });
          }
        });
      });
    }

    const agregadas = d3.rollups(
      entidadesConectadas,
      (v) => v.length,
      (d) => d.fecha,
      (d) => d.serie
    );

    const resultado: { fecha: Date; serie: string; total: number }[] = [];
    agregadas.forEach(([fecha, seriesInternas]) => {
      seriesInternas.forEach(([serie, total]) => {
        resultado.push({
          fecha: new Date(fecha),
          serie,
          total,
        });
      });
    });

    return resultado;
  }
}
