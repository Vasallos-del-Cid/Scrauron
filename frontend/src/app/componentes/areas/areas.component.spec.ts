import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AreasComponent } from './areas.component';

describe('InteresesComponent', () => {
  let component: AreasComponent;
  let fixture: ComponentFixture<AreasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AreasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AreasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
