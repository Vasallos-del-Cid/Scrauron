import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PruebaGridComponent } from './prueba-grid.component';

describe('PruebaGridComponent', () => {
  let component: PruebaGridComponent;
  let fixture: ComponentFixture<PruebaGridComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PruebaGridComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PruebaGridComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
