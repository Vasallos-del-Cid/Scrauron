import { Injectable } from '@angular/core';
import { Fuente } from './fuente.model';
import { CrudService } from '../../core/services/api-service/crud-service.abstract';
import { ApiService } from '../../core/services/api-service/api-service.service';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class FuenteService extends CrudService<Fuente> {
  constructor(http: HttpClient) {
    super(new ApiService<Fuente>(http, 'fuentes'));
  }
}
