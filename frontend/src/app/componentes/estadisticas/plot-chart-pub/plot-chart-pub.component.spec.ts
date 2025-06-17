import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GraficoBarrasComponent } from './plot-chart-pub.component';

describe('PlotChartComponent', () => {
  let component: GraficoBarrasComponent;
  let fixture: ComponentFixture<GraficoBarrasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GraficoBarrasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GraficoBarrasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
