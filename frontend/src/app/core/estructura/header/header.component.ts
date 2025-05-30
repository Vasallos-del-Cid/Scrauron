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
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
  encapsulation: ViewEncapsulation.None,
  imports: [SidebarModule, AccordionModule, RouterModule],
})
export class HeaderComponent {
  constructor(private _router: Router) {
    this.clicked = this.clicked.bind(this);
  }

  @ViewChild('sidebar') public sidebarObj?: SidebarComponent;
  @ViewChild('accordion') public accordionObj?: AccordionComponent;

  public data: { [key: string]: Object }[] = [
    {
      header: '<i class="e-icons e-home"></i> Inicio',
      content: '<div id="home_Items"></div>',
      subItems: [{ header: '<i class="e-icons e-home"></i> Home' }],
    },
    {
      header: '<i class="e-icons e-bookmark"></i> Gestión',
      content: '<div id="gestion_Items"></div>',
      subItems: [
        { header: '<i class="e-icons e-bookmark"></i> Conceptos' },
        { header: '<i class="e-icons e-eye"></i> Fuentes' },
        { header: '<i class="e-icons e-location"></i> Areas' },
      ],
    },
    {
      header: '<i class="e-icons e-border-shadow-1"></i> Publicaciones',
      content: '<div id="alertas_Items"></div>',
      subItems: [{ header: '<i class="e-icons e-web-layout"></i> Ver publicaciones' }],
    },
    {
      header: '<i class="e-icons e-user"></i> Perfil',
      content: '<div id="perfil_Items"></div>',
      subItems: [{ header: '<i class="e-icons e-user"></i> Mi perfil' }],
    },
  ];

  public expand(e: ExpandEventArgs): void {
    if (e.isExpanded) {
      if (
        (e.element as HTMLElement)
          .getElementsByClassName('e-acrdn-content')[0]
          .children[0].classList.contains('e-accordion')
      ) {
        return;
      }
      let nestAcrdn: Accordion = new Accordion({
        items: (<{ subItems: object[] }>e.item).subItems,
        expanding: this.expand,
        clicked: this.clicked,
      });

      let elemId: string = (e.element as HTMLElement).getElementsByClassName(
        'e-acrdn-content'
      )[0].children[0].id;
      nestAcrdn.appendTo('#' + elemId);
    }
  }

  public clicked(e: AccordionClickArgs): void {
    const cleanHeader = (e.item?.header as string)
      .replace(/<[^>]*>/g, '')
      .trim(); // Quita HTML
    switch (cleanHeader) {
      case 'Home':
        this._router.navigate(['/']);
        this.sidebarObj?.hide();
        break;
      case 'Conceptos':
        this._router.navigate(['/conceptos']);
        this.sidebarObj?.hide();
        break;
      case 'Fuentes':
        this._router.navigate(['/fuentes']);
        this.sidebarObj?.hide();
        break;
      case 'Areas':
        this._router.navigate(['/areas']);
        this.sidebarObj?.hide();
        break;
      case 'Ver publicaciones':
        this._router.navigate(['/publicaciones']);
        this.sidebarObj?.hide();
        break;
      case 'Mi perfil':
        this._router.navigate(['/perfil']);
        this.sidebarObj?.hide();
        break;
    }
  }

  public hamburgerClick(): void {
    this.sidebarObj?.show();
    this.accordionObj?.refresh();
  }

  public close(): void {
    this.sidebarObj?.hide();
  }
}
