import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.css'
})
export class AuthComponent {
  email = '';
  password = '';
  mode: 'login' | 'register' = 'login';
  loading = false;
  error = '';

  constructor(private apiService: ApiService, private router: Router) {}

  submit() {
    this.error = '';
    this.loading = true;
    const handler = this.mode === 'login'
      ? this.apiService.login(this.email, this.password)
      : this.apiService.register(this.email, this.password);

    handler.subscribe({
      next: (response) => {
        if (response.success) {
          this.apiService.setToken(response.token);
          this.router.navigate(['/report']);
        } else {
          this.error = 'Authentication failed.';
        }
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.error || 'Authentication error';
        this.loading = false;
      }
    });
  }
}
