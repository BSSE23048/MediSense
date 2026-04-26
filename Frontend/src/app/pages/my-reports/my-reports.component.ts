import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, ReportListItem } from '../../services/api.service';

@Component({
  selector: 'app-my-reports',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './my-reports.component.html',
  styleUrl: './my-reports.component.css'
})
export class MyReportsComponent implements OnInit {
  reports: ReportListItem[] = [];
  selectedReport: any = null;
  error = '';
  loading = false;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports() {
    if (!this.apiService.isLoggedIn()) {
      this.error = 'Please login to access saved reports.';
      return;
    }
    this.loading = true;
    this.apiService.listReports().subscribe({
      next: (response) => {
        this.reports = response.reports || [];
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.error || 'Failed to load reports';
        this.loading = false;
      }
    });
  }

  openReport(reportId: number) {
    this.apiService.getReport(reportId).subscribe({
      next: (response) => {
        this.selectedReport = response.report;
      },
      error: (err) => {
        this.error = err.error?.error || 'Failed to open report';
      }
    });
  }
}
