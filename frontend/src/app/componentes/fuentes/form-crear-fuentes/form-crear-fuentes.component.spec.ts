import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FormCrearFuentesComponent } from './form-crear-fuentes.component';

describe('FormCrearFuentesComponent', () => {
  let component: FormCrearFuentesComponent;
  let fixture: ComponentFixture<FormCrearFuentesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FormCrearFuentesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FormCrearFuentesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
