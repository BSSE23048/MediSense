import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-loader',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="loader-container">
      <div class="spinner"></div>
      <p class="loader-text" *ngIf="message">{{ message }}</p>
    </div>
  `,
  styles: [`
    .loader-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px;
      gap: 24px;
    }

    .spinner {
      width: 50px;
      height: 50px;
      border: 3px solid var(--border-color);
      border-top-color: var(--primary-text);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .loader-text {
      color: var(--secondary-text);
      font-size: 0.95rem;
      text-align: center;
    }
  `]
})
export class LoaderComponent {
  message: string = '';
}
