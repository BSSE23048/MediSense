import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-text-slider',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './text-slider.component.html',
  styleUrl: './text-slider.component.css'
})
export class TextSliderComponent {
  @Input() text: string = '';
}
