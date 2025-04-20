import { Component } from '@angular/core';
import { GridModule, PagerModule } from '@syncfusion/ej2-angular-grids';

import { RouterOutlet } from '@angular/router';

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
}
