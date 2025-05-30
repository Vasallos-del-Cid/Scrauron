import { Injectable } from '@angular/core';
import { DataService } from '../../core/services/data-service/data-service.service';
import { HttpClient } from '@angular/common/http';
import { Conceptos } from './Conceptos.model';

@Injectable({
  providedIn: 'root',
})
export class ConceptosService extends DataService<Conceptos> {
  constructor(http: HttpClient) {
    super(http, 'conceptos');
  }
}
