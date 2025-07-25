import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { DataService } from '../../../core/services/data-service/data-service.service';
import { Publicacion } from './publicacion.model';
import { Observable, forkJoin } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class PublicacionesService extends DataService<Publicacion> {
  constructor(http: HttpClient) {
    super(http, 'publicacionesconceptos');
  }

  getFiltradas(filtros: {
    fechaDesde: Date;
    fechaHasta: Date;
    tono?: string;
    busqueda_palabras?: string;
    fuente_id?: string;
    keywords?: string[];
    concepto_interes?: string;
    area_id?: string;
    pais?: string;
    page?: number;
    pageSize?: number;
  }): Observable<{ total: number; publicaciones: Publicacion[] }> {
    const cleanISO = (date: Date) => date.toISOString().replace('Z', '');

    let params = new HttpParams()
      .set('fechaInicio', cleanISO(filtros.fechaDesde))
      .set('fechaFin', cleanISO(filtros.fechaHasta));

    if (filtros.tono != null) params = params.set('tono', filtros.tono);
    if (filtros.busqueda_palabras) params = params.set('busqueda_palabras', filtros.busqueda_palabras);
    if (filtros.concepto_interes) params = params.set('concepto_interes', filtros.concepto_interes);
    else if (filtros.area_id) params = params.set('area_id', filtros.area_id);
    if (filtros.fuente_id) params = params.set('fuente_id', filtros.fuente_id);
    if (filtros.pais) params = params.set('pais', filtros.pais);
    if (filtros.page) params = params.set('page', filtros.page.toString());
    if (filtros.pageSize) params = params.set('pageSize', filtros.pageSize.toString());
    if (filtros.keywords) {
      filtros.keywords.forEach(k => {
        params = params.append('keywordsRelacionadas', k);
      });
    }

    return this.http.get<{ total: number; publicaciones: Publicacion[] }>(
      `${this.baseUrl}/publicaciones_filtradas`, { params }
    );
  }

  getConceptosArea(areaId: string): Observable<any[]> {
    const params = new HttpParams().set('area_id', areaId);
    return this.http.get<any[]>(`${this.baseUrl}/conceptos/area`, { params });
  }

  getAreas(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/areas`);
  }

  getFuentes(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/fuentes`);
  }

  getConceptosYAreas(areaId: string): Observable<any> {
    return forkJoin({
      areas: this.getAreas(),
      conceptos: this.getConceptosArea(areaId)
    });
  }
  eliminarConcepto(pubId: string, conceptoId: string) {
    return this.http.delete(`${this.baseUrl}/publicaciones/${pubId}/conceptos/${conceptoId}`);
  }
  generarInformeImpactoTemporal(filtros: {
    fechaDesde: Date;
    fechaHasta: Date;
    tono?: string;
    busqueda_palabras?: string;
    fuente_id?: string;
    concepto_interes?: string;
    area_id?: string;
    pais?: string;
  }): Observable<Blob> {
    const cleanISO = (date: Date) => date.toISOString().replace('Z', '');

    let params = new HttpParams()
      .set('fechaInicio', cleanISO(filtros.fechaDesde))
      .set('fechaFin', cleanISO(filtros.fechaHasta));

    if (filtros.tono) params = params.set('tono', filtros.tono);
    if (filtros.busqueda_palabras) params = params.set('busqueda_palabras', filtros.busqueda_palabras);
    if (filtros.fuente_id) params = params.set('fuente_id', filtros.fuente_id);
    if (filtros.concepto_interes) params = params.set('concepto_interes', filtros.concepto_interes);
    if (filtros.area_id) params = params.set('area_id', filtros.area_id);
    if (filtros.pais) params = params.set('pais', filtros.pais);

    return this.http.get(`${this.baseUrl}/generar_informe_impacto_temporal`, {
      params,
      responseType: 'blob'
    });
  }

  getPublicacionesPorDia(params: any) {
    return this.http.get<{ datoX: string; datoY: number }[]>(`${this.baseUrl}/publicaciones_dia`, { params });
  }
  getTonoMedioPorDia(params: any) {
    return this.http.get<{ datoX: string; datoY: number }[]>(`${this.baseUrl}/tono_medio_dia`, { params });
  }
  getPublicacionesPorPais(params: any) {
    return this.http.get<{ datoX: string; datoY: number }[]>(`${this.baseUrl}/publicaciones_pais`, { params });
  }
  getTonoMedioPorPais(params: any) {
    return this.http.get<{ datoX: string; datoY: number }[]>(`${this.baseUrl}/tono_medio_pais`, { params });
  }

} 
