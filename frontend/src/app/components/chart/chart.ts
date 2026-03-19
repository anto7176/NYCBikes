import { Component, input } from '@angular/core';
import { ChartModule } from 'primeng/chart';
import { ChartData } from '../../models/chart-data';

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
  
  public readonly data = input.required<ChartData>();

  public readonly basicOptions = {
    maintainAspectRatio: false,
    aspectRatio: 0.8,
    plugins: {
        legend: {
            labels: {
                color: 'white'
            }
        }
    },
    scales: {
        x: {
            ticks: {
                color: 'white'
            },
            grid: {
                color: 'white'
            }
        },
        y: {
            beginAtZero: true,
            ticks: {
                color: 'white'
            },
            grid: {
                color: 'transparent'
            }
        }
    }
  };
}
