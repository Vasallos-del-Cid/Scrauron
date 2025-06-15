import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DataService } from '../../../core/services/data-service/data-service.service';
import { Publicacion } from './publicacion.model';


@Injectable({
  providedIn: 'root',
})
export class PublicacionesService extends DataService<Publicacion> {
  constructor(http: HttpClient) {
    super(http, 'publicacionesconceptos');
  }
}
