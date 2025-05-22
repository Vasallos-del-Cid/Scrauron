import { Injectable } from '@angular/core';
import { DataService } from '../../core/services/data-service/data-service.service';
import { HttpClient } from '@angular/common/http';
import { Areas } from './areas.model';

@Injectable({
  providedIn: 'root',
})
export class AreasService extends DataService<Areas> {
  constructor(http: HttpClient) {
    super(http, 'areas');
  }
}
