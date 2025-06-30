import { Injectable } from '@angular/core';
import { DataService } from '../../core/services/data-service/data-service.service';
import { HttpClient } from '@angular/common/http';
import { Conceptos } from './Conceptos.model';
import { Observable } from 'rxjs';
import { Keyword } from './Keyword.model';

@Injectable({
  providedIn: 'root',
})
export class ConceptosService extends DataService<Conceptos> {
  constructor(http: HttpClient) {
    super(http, 'conceptos');
  }

  override getAll(): Observable<Conceptos[]> {
    return this.http.get<Conceptos[]>(`${this.baseUrl}/conceptos`);
  }

  getById(id: string): Observable<Conceptos> {
    return this.http.get<Conceptos>(`${this.baseUrl}/conceptos/${id}`);
  }

  createOnlyName(nombre: string): Observable<{ _id: string }> {
    return this.http.post<{ _id: string }>(`${this.baseUrl}/conceptos`, { nombre });
  }

  generateDescription(id: string): Observable<Partial<Conceptos>> {
    return this.http.patch<Partial<Conceptos>>(
      `${this.baseUrl}/conceptos/${id}/generar_descripcion`, {}
    );
  }

  generateKeywords(id: string, descripcion: string): Observable<{ keywords_ids: string[] }> {
    return this.http.patch<{ keywords_ids: string[] }>(
      `${this.baseUrl}/conceptos/${id}/generar_keywords`,
      { descripcion }
    );
  }

  fetchKeywordsByConcept(id: string): Observable<Keyword[]> {
    return this.http.get<Keyword[]>(`${this.baseUrl}/keywords/concepto`, {
      params: { concepto_id: id }
    });
  }

  createKeyword(nombre: string): Observable<Keyword> {
    return this.http.post<Keyword>(`${this.baseUrl}/keywords`, { nombre });
  }

  acceptKeywords(areaId: string, body: {
    _id: string;
    nombre: string;
    descripcion: string;
    keywords_ids: string[];
  }): Observable<Conceptos> {
    return this.http.patch<Conceptos>(
      `${this.baseUrl}/conceptos/${areaId}/keywords_aceptadas`, body
    );
  }
  
}
