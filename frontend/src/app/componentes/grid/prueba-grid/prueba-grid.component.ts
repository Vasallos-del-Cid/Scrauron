import { Component } from '@angular/core';

import {
  GridModule,
  PagerModule,
  PageSettingsModel,
} from '@syncfusion/ej2-angular-grids';
import { data } from './datasource';

@Component({
  selector: 'app-prueba-grid',
  imports: [GridModule, PagerModule],
  standalone: true,
  templateUrl: './prueba-grid.component.html',
  styleUrl: './prueba-grid.component.css',
})
export class PruebaGridComponent {
  public data?: object[];
  public pageSettings?: PageSettingsModel;

  ngOnInit(): void {
    this.data = data;

    // The pageSettings property is also set to specify the page size for the Grid
    this.pageSettings = { pageSize: 10 };
  }
}
