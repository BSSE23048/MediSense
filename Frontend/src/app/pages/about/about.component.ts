import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TextSliderComponent } from '../../components/text-slider/text-slider.component';

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [CommonModule, TextSliderComponent],
  templateUrl: './about.component.html',
  styleUrl: './about.component.css'
})
export class AboutComponent {
  features = [
    {
      icon: 'scan',
      title: 'Advanced OCR',
      description: 'State-of-the-art text extraction from medical documents using Tesseract and EasyOCR'
    },
    {
      icon: 'brain',
      title: 'AI-Powered Analysis',
      description: 'Leveraging Google Gemini and GPT for intelligent medical report summarization'
    },
    {
      icon: 'database',
      title: 'RAG Technology',
      description: 'Retrieval Augmented Generation using verified WHO and NIH medical databases'
    },
    {
      icon: 'shield-check',
      title: 'Secure Processing',
      description: 'Enterprise-grade security with encrypted data transmission and storage'
    }
  ];

  techStack = [
    { category: 'Frontend', items: ['Angular 19', 'TypeScript', 'Phosphor Icons'] },
    { category: 'Backend', items: ['Flask', 'Python', 'LangChain'] },
    { category: 'AI/ML', items: ['Google Gemini', 'ChromaDB', 'SentenceTransformers'] },
    { category: 'OCR', items: ['Tesseract', 'EasyOCR', 'PyPDF2'] }
  ];
}
