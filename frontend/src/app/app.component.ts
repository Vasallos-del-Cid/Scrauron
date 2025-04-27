import { Component } from '@angular/core';
import {
  ButtonModule,
  CheckBoxModule,
  RadioButtonModule,
  SwitchModule,
  ChipListModule,
  FabModule,
  SpeedDialModule,
  SmartPasteButtonModule,
} from '@syncfusion/ej2-angular-buttons';
import {
  DropDownListModule,
  ComboBoxModule,
  AutoCompleteModule,
  MultiSelectModule,
  ListBoxModule,
  DropDownTreeModule,
  MentionModule,
} from '@syncfusion/ej2-angular-dropdowns';
import { ListViewModule } from '@syncfusion/ej2-angular-lists';
import {
  DropDownButtonModule,
  SplitButtonModule,
  ProgressButtonModule,
} from '@syncfusion/ej2-angular-splitbuttons';
import {
  AccordionModule,
  ToolbarModule,
  ContextMenuModule,
  BreadcrumbModule,
  CarouselModule,
  TabModule,
  TreeViewModule,
  SidebarModule,
  MenuModule,
  AppBarModule,
  StepperModule,
} from '@syncfusion/ej2-angular-navigations';

import { HeaderComponent } from './core/estructura/header/header.component';
import { BodyComponent } from './core/estructura/body/body.component';
import { FooterComponent } from './core/estructura/footer/footer.component';
import { RouterOutlet, RouterModule } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [
    ButtonModule,
    CheckBoxModule,
    RadioButtonModule,
    SwitchModule,
    ChipListModule,
    FabModule,
    SpeedDialModule,
    SmartPasteButtonModule,
    DropDownListModule,
    ComboBoxModule,
    AutoCompleteModule,
    MultiSelectModule,
    ListBoxModule,
    DropDownTreeModule,
    MentionModule,
    ListViewModule,
    DropDownButtonModule,
    SplitButtonModule,
    ProgressButtonModule,
    AccordionModule,
    ToolbarModule,
    ContextMenuModule,
    BreadcrumbModule,
    CarouselModule,
    TabModule,
    TreeViewModule,
    SidebarModule,
    MenuModule,
    AppBarModule,
    StepperModule,
    HeaderComponent,
    BodyComponent,
    FooterComponent,
    //RouterOutlet,
    RouterModule,
    
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'Rodrigo';
}
