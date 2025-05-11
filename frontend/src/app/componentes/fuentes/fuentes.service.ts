import { Injectable } from '@angular/core';
import { Fuente } from './fuente.model';
import { HttpClient } from '@angular/common/http';
import { DataService } from '../../core/services/data-service/data-service.service';


/**
 * Servicio para manejar la lógica de negocio de las fuentes
 * 
 * usa el servicio base {@link DataService} para manejar la lógica CRUD
 */
@Injectable({ providedIn: 'root' })
export class FuenteService extends DataService<Fuente> {
  constructor(http: HttpClient) {
    super(http, 'fuentes');
  }
}
