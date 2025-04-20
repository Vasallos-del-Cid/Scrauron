import { Component } from '@angular/core';

import { HeaderComponent } from "./core/estructura/header/header.component";
import { BodyComponent } from "./core/estructura/body/body.component";
import { FooterComponent } from "./core/estructura/footer/footer.component";

@Component({
  selector: 'app-root',
  imports: [
    HeaderComponent,
    BodyComponent,
    FooterComponent
],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'Rodrigo';

   
}
