import { Injectable } from '@angular/core';
import { DataService } from '../../core/services/data-service/data-service.service';
import { HttpClient } from '@angular/common/http';
import { Intereses } from './Intereses.model';

@Injectable({
  providedIn: 'root',
})
export class InteresesService extends DataService<Intereses> {
  constructor(http: HttpClient) {
    super(http, 'conceptos');
  }
}
