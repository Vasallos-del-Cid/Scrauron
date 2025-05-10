import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiOptions, ApiService } from '../../core/services/api-service/api-service.component';
import { Fuente } from './fuente.model';

@Injectable({
  providedIn: 'root'
})
export class FuenteService extends ApiService<Fuente> {
  constructor(http: HttpClient) {
    super(http, 'fuentes');
  }

  getFuentes( success: (data: Fuente[]) => void): void {
    this.getAll<Fuente>({ success }).subscribe();
  }

  createFuente(fuente: Fuente, options?: ApiOptions<Fuente>): void {
    this.create<Fuente>(fuente, options).subscribe();
  }

  updateFuente(id: string, parcial: Partial<Fuente>, options?: ApiOptions<Fuente>): void {
    this.update<Fuente>(id, parcial, options).subscribe();
  }

  deleteFuente(id: string, success: () => void): void {
    this.delete(id, { success }).subscribe();
  }

  getFuente(id: string, success: (data: Fuente) => void): void {
    this.getOne<Fuente>(id, { success }).subscribe();
  }
}
