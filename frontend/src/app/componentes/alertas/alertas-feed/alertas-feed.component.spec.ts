import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlertasFeedComponent } from './alertas-feed.component';

describe('AlertasFeedComponent', () => {
  let component: AlertasFeedComponent;
  let fixture: ComponentFixture<AlertasFeedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlertasFeedComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AlertasFeedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
