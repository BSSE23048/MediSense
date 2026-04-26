import { Component, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TextSliderComponent } from '../../components/text-slider/text-slider.component';

declare var Chart: any;

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink, TextSliderComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements AfterViewInit {
  @ViewChild('diseaseChart') diseaseChart!: ElementRef<HTMLCanvasElement>;
  @ViewChild('accessChart') accessChart!: ElementRef<HTMLCanvasElement>;
  @ViewChild('accuracyChart') accuracyChart!: ElementRef<HTMLCanvasElement>;
  features = [
    {
      icon: 'file-text',
      title: 'Report Analysis',
      description: 'Upload medical reports and get AI-powered summaries in both patient-friendly and technical formats'
    },
    {
      icon: 'heartbeat',
      title: 'Symptom Checker',
      description: 'Describe your symptoms and receive evidence-based analysis with risk assessment'
    },
    {
      icon: 'shield-check',
      title: 'Secure & Private',
      description: 'Your health data is processed securely with enterprise-grade encryption'
    }
  ];

  stats = [
    { value: '10K+', label: 'Reports Analyzed' },
    { value: '98%', label: 'Accuracy Rate' },
    { value: '24/7', label: 'Availability' }
  ];

  ngAfterViewInit() {
    this.initCharts();
  }

  initCharts() {
    // Disease Prevalence Chart
    new Chart(this.diseaseChart.nativeElement, {
      type: 'bar',
      data: {
        labels: ['Diabetes', 'Hypertension', 'Heart Disease', 'Cancer', 'Respiratory'],
        datasets: [{
          label: 'Cases per 100k',
          data: [10500, 31400, 6950, 4420, 8100],
          backgroundColor: 'rgba(25, 167, 206, 0.8)',
          borderColor: '#19A7CE',
          borderWidth: 2,
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(11, 36, 71, 0.95)',
            titleColor: '#ffffff',
            bodyColor: '#D2E9E9',
            borderColor: '#19A7CE',
            borderWidth: 2
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(11, 36, 71, 0.1)' },
            ticks: { color: '#334155', font: { size: 12 } }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#334155', font: { size: 12 } }
          }
        }
      }
    });

    // Healthcare Accessibility Chart
    new Chart(this.accessChart.nativeElement, {
      type: 'doughnut',
      data: {
        labels: ['Urban Access', 'Rural Access', 'Limited Access', 'No Access'],
        datasets: [{
          data: [45, 30, 18, 7],
          backgroundColor: [
            'rgba(25, 167, 206, 0.8)',
            'rgba(11, 36, 71, 0.8)',
            'rgba(210, 233, 233, 0.8)',
            'rgba(239, 68, 68, 0.8)'
          ],
          borderColor: '#FFFFFF',
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#334155', padding: 15, font: { size: 12 } }
          },
          tooltip: {
            backgroundColor: 'rgba(11, 36, 71, 0.95)',
            titleColor: '#ffffff',
            bodyColor: '#D2E9E9',
            borderColor: '#19A7CE',
            borderWidth: 2
          }
        }
      }
    });

    // AI Accuracy Chart
    new Chart(this.accuracyChart.nativeElement, {
      type: 'line',
      data: {
        labels: ['2020', '2021', '2022', '2023', '2024'],
        datasets: [{
          label: 'Accuracy %',
          data: [87, 91, 94, 96, 98],
          borderColor: '#19A7CE',
          backgroundColor: 'rgba(25, 167, 206, 0.2)',
          tension: 0.4,
          fill: true,
          borderWidth: 3,
          pointBackgroundColor: '#19A7CE',
          pointBorderColor: '#FFFFFF',
          pointBorderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(11, 36, 71, 0.95)',
            titleColor: '#ffffff',
            bodyColor: '#D2E9E9',
            borderColor: '#19A7CE',
            borderWidth: 2
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            min: 80,
            max: 100,
            grid: { color: 'rgba(11, 36, 71, 0.1)' },
            ticks: { color: '#334155', font: { size: 12 } }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#334155', font: { size: 12 } }
          }
        }
      }
    });
  }
}
