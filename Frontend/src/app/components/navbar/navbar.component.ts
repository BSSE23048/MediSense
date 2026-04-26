import { Component, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent {
  isScrolled = false;
  private lastScrollY = window.scrollY;
  private isMobile = window.innerWidth <= 768;

  @HostListener('window:scroll', [])
  onWindowScroll() {
    const currentScrollY = window.scrollY;
    if (this.isMobile) {
      if (currentScrollY > 30 && currentScrollY > this.lastScrollY) {
        this.isScrolled = true;
      } else if (currentScrollY < this.lastScrollY) {
        this.isScrolled = false;
      } else if (currentScrollY <= 30) {
        this.isScrolled = false;
      }
    } else {
      if (currentScrollY > 50 && currentScrollY > this.lastScrollY) {
        this.isScrolled = true;
      } else if (currentScrollY < this.lastScrollY) {
        this.isScrolled = false;
      } else if (currentScrollY <= 50) {
        this.isScrolled = false;
      }
    }
    this.lastScrollY = currentScrollY;
  }

  @HostListener('window:resize', [])
  onResize() {
    this.isMobile = window.innerWidth <= 768;
  }

  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}
