import { Component, input } from '@angular/core';
import { ChartModule } from 'primeng/chart';
import { ChatData } from '../../models/chart-data';

@Component({
  selector: 'app-chart',
  imports: [
    ChartModule
  ],
  templateUrl: './chart.html',
  styleUrl: './chart.css',
})
export class Chart {
  //
  //   Interfaces
  //
  
  public readonly data = input.required<ChatData>();
}
