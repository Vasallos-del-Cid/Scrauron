import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders,
} from '@angular/common/http';
import { Observable, catchError, finalize, tap, throwError } from 'rxjs';

export interface ApiOptions<T> {
  success?: (data: T) => void;
  failure?: (error: any) => void;
  callback?: () => void;
  silent?: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class ApiService<T> {
  private readonly httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
  };

  private readonly baseUrl: String;
  private readonly endpoint: String;

  constructor(
    protected http: HttpClient,
    endpoint: String,
    baseUrl: String = 'http://localhost:5000/api'
  ) {
    this.endpoint = endpoint;
    this.baseUrl = baseUrl;
  }

  getAll<T>(options?: ApiOptions<T[]>): Observable<T[]> {
    return this.http
      .get<T[]>(`${this.baseUrl}/${this.endpoint}`, this.httpOptions)
      .pipe(
        tap((data) => options?.success?.(data)),
        catchError((error) => this.handleError(error, options)),
        finalize(() => options?.callback?.())
      );
  }

  getOne<T>(id: string, options?: ApiOptions<T>): Observable<T> {
    return this.http
      .get<T>(`${this.baseUrl}/${this.endpoint}/${id}`, this.httpOptions)
      .pipe(
        tap((data) => options?.success?.(data)),
        catchError((error) => this.handleError(error, options)),
        finalize(() => options?.callback?.())
      );
  }

  create<T>(item: T, options?: ApiOptions<T>): Observable<T> {
    return this.http
      .post<T>(`${this.baseUrl}/${this.endpoint}`, item, this.httpOptions)
      .pipe(
        tap((data) => options?.success?.(data)),
        catchError((error) => this.handleError(error, options)),
        finalize(() => options?.callback?.())
      );
  }

  update<T>(
    id: string,
    item: Partial<T>,
    options?: ApiOptions<T>
  ): Observable<T> {
    return this.http
      .patch<T>(
        `${this.baseUrl}/${this.endpoint}/${id}`,
        item,
        this.httpOptions
      )
      .pipe(
        tap((data) => options?.success?.(data)),
        catchError((error) => this.handleError(error, options)),
        finalize(() => options?.callback?.())
      );
  }

  delete(id: string, options?: ApiOptions<void>): Observable<void> {
    return this.http
      .delete<void>(`${this.baseUrl}/${this.endpoint}/${id}`, this.httpOptions)
      .pipe(
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
        'Ocurrió un error en la comunicación con el servidor';
      alert(userMessage);
    }
    options?.failure?.(error);
    return throwError(() => error);
  }
}
