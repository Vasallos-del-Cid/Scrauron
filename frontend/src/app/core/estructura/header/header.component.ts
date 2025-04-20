import { Component, ViewEncapsulation, Inject, ViewChild } from '@angular/core';
import {
  SidebarComponent,
  SidebarModule,
  AccordionModule,
  ExpandEventArgs,
  Accordion,
  AccordionClickArgs,
  AccordionComponent,
  ClickEventArgs,
} from '@syncfusion/ej2-angular-navigations';
import { Router, RouterModule } from '@angular/router';
import { ListViewModule } from '@syncfusion/ej2-angular-lists';
import { from } from 'rxjs';

@Component({
  selector: 'app-header',
  imports: [SidebarModule, AccordionModule, RouterModule],
  templateUrl: './header.component.html',
  encapsulation: ViewEncapsulation.None,
  styleUrl: './header.component.css',
})
export class HeaderComponent {
  constructor(private _router: Router) {

     // Vincular el método al contexto de la clase para que este método pueda acceder a las propiedades de la clase
    this.clicked = this.clicked.bind(this);
  }

  @ViewChild('sidebar')
  public sidebarObj?: SidebarComponent;
  @ViewChild('accordion')
  public accordionObj?: AccordionComponent;

  public data: { [key: string]: Object }[] = [
    {
      header: 'Grid',
      content: '<div id="Appliances_Items"></div>',
      subItems: [
        {
          header: 'Kitchen',
          content: '<div id="Appliances_Kitchen_Items"></div>',
          subItems: [
            {
              header: 'home',
            },
            {
              header: 'Grid',
            },
            { header: 'Blenders' },
          ],
        },
      ],
    },
  ];

  //Expanding Event function for Accordion component.
  public expand(e: ExpandEventArgs): void {
    if (e.isExpanded) {
      if (
        (e.element as HTMLElement)
          .getElementsByClassName('e-acrdn-content')[0]
          .children[0].classList.contains('e-accordion')
      ) {
        return;
      }
      //Initialize Nested Accordion component
      let nestAcrdn: Accordion = new Accordion({
        items: (<{ subItems: object[] }>e.item).subItems,
        expanding: this.expand,
        clicked: this.clicked,
      });

      let elemId: string = (e.element as HTMLElement).getElementsByClassName(
        'e-acrdn-content'
      )[0].children[0].id;
      //Render initialized Nested Accordion component
      nestAcrdn.appendTo('#' + elemId);
    }
  }

  public clicked(e: AccordionClickArgs): void {
    switch (e.item?.header?.toString()) {
      case 'home':
        this._router.navigate(['/']);
        break;
      case 'Grid':
        this._router.navigate(['/grid']);
        break;
    }
  }

  public hamburgerClick(): void {
    this.sidebarObj?.show();
    (this.accordionObj as AccordionComponent).refresh();
  }

  public close(): void {
    this.sidebarObj?.hide();
  }
}
