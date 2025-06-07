import { Injectable } from '@angular/core';
import * as d3 from 'd3';

@Injectable({
  providedIn: 'root',
})
export class DataTrasnformerService {
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

  transformarPorEntidad<T>(
    publicaciones: any[],
    entidades: any[],
    campoRelacion: string,
    campoNombre: string,
    aggregator: (
      items: { fecha: string; serie: string; tono?: number }[]
    ) => number
  ): Array<{ fecha: Date; serie: string; valor: number }> {
    const pubs = publicaciones
      .filter(
        (p): p is { _id: string; fecha: string; tono?: number } =>
          typeof p._id === 'string'
      )
      .map((p) => ({ _id: p._id, fecha: p.fecha, tono: p.tono }));

    // 2) Mapas para lookup
    const entidadMap = new Map(
      entidades.map((e: any) => [e._id, e[campoNombre]])
    );
    const pubMap = new Map(pubs.map((p) => [p._id, p]));

    // 3) Construir array intermedio { fecha, serie, tono }
    const intermedio: { fecha: string; serie: string; tono?: number }[] = [];
    entidades.forEach((ent: any) => {
      const serie = entidadMap.get(ent._id) || ent._id;
      const relacionados: string[] = ent[campoRelacion] || [];
      relacionados.forEach((pubId) => {
        const pub = pubMap.get(pubId);
        if (pub) {
          intermedio.push({
            fecha: d3.timeFormat('%Y-%m-%d')(new Date(pub.fecha)),
            serie,
            tono: pub.tono,
          });
        }
      });
    });

    // 4) Rollup
    const rollup = d3.rollups(
      intermedio,
      (v) => aggregator(v),
      (d) => d.fecha,
      (d) => d.serie
    );

    // 5) Aplanar y parsear fecha
    const resultado: { fecha: Date; serie: string; valor: number }[] = [];
    rollup.forEach(([fechaStr, seriesArr]) => {
      seriesArr.forEach(([serie, valor]) => {
        resultado.push({
          fecha: new Date(fechaStr),
          serie,
          valor,
        });
      });
    });
    return resultado;
  }
}
