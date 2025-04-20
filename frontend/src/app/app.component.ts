import { Component } from '@angular/core';
import { GridModule, PagerModule } from '@syncfusion/ej2-angular-grids';

import { RouterOutlet } from '@angular/router';

import { PageSettingsModel } from '@syncfusion/ej2-angular-grids';
import { data } from './datasource';

@Component({
  selector: 'app-root',
  imports: [
    GridModule,
    PagerModule,
    RouterOutlet
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'frontend';

    public data?: object[];
  public pageSettings?: PageSettingsModel;
  
  ngOnInit(): void {
    this.data = data;

    // The pageSettings property is also set to specify the page size for the Grid
    this.pageSettings = { pageSize: 10 };
  }
}
