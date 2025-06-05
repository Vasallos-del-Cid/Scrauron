import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MultiLineaComponent } from './multi-linea.component';

describe('MultiLineaComponent', () => {
  let component: MultiLineaComponent;
  let fixture: ComponentFixture<MultiLineaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MultiLineaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MultiLineaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
