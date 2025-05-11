import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders,
} from '@angular/common/http';
import { Observable, catchError, finalize, tap, throwError } from 'rxjs';
import { ApiOptions } from './api-options.interface';
/**
 * Clase ApiService
 * 
 * Esta clase es un servicio genérico para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) en una API RESTful.
 * 
 * los metodos admiten un objeto de opciones ApiOptions que permite definir success, failure y callback para el éxito el error y para ejecutar siempre, así como una opción para silenciar los mensajes de error.
 * 
 * Ver: {@link  ApiOptions}
 */
@Injectable({
  providedIn: 'root',
})
export class ApiService<T> {
  private readonly httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
  };

  private readonly baseUrl: String;
  private readonly endpoint: String;
  private readonly url: String;

  constructor(
    protected http: HttpClient,
    endpoint: String,
    baseUrl: String = 'http://localhost:5000/api'
  ) {
    this.endpoint = endpoint;
    this.baseUrl = baseUrl;
    this.url = `${this.baseUrl}/${this.endpoint}`;
  }

  getAll<T>(options?: ApiOptions<T[]>): Observable<T[]> {
    return this.http.get<T[]>(`${this.url}`, this.httpOptions).pipe(
      tap((data) => options?.success?.(data)),
      catchError((error) => this.handleError(error, options)),
      finalize(() => options?.callback?.())
    );
  }

  getOne<T>(id: string, options?: ApiOptions<T>): Observable<T> {
    return this.http.get<T>(`${this.url}/${id}`, this.httpOptions).pipe(
      tap((data) => options?.success?.(data)),
      catchError((error) => this.handleError(error, options)),
      finalize(() => options?.callback?.())
    );
  }

  create<T>(item: T, options?: ApiOptions<T>): Observable<T> {
    return this.http.post<T>(`${this.url}`, item, this.httpOptions).pipe(
      tap((data) => options?.success?.(data)),
      catchError((error) => this.handleError(error, options)),
      finalize(() => options?.callback?.())
    );
  }

  update<T>(
    id: string,
    item: Partial<T>,
    options?: ApiOptions<T>
  ): Observable<any> {
    return this.http.patch<T>(`${this.url}/${id}`, item, this.httpOptions).pipe(
      tap((data) => options?.success?.(data)),
      catchError((error) => this.handleError(error, options)),
      finalize(() => options?.callback?.())
    );
  }

  delete(id: string, options?: ApiOptions<void>): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`, this.httpOptions).pipe(
      tap(() => options?.success?.()),
      catchError((error) => this.handleError(error, options)),
      finalize(() => options?.callback?.())
    );
  }

  private handleError(error: HttpErrorResponse, options?: ApiOptions<any>) {
    console.error('❌ API Error:', error);
    if (!options?.silent) {
      const userMessage =
        error.error?.error ||
        error.error ||
        'Ocurrió un error en la comunicación con el servidor';
      alert(userMessage);
    }
    options?.failure?.(error);
    return throwError(() => error);
  }
}
