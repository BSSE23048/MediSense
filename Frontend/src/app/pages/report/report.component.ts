import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, SummaryResponse, MedicineDetail } from '../../services/api.service';
import { VoiceAssistantService } from '../../services/voice-assistant.service';
import { LoaderComponent } from '../../components/loader/loader.component';
import { TextSliderComponent } from '../../components/text-slider/text-slider.component';

@Component({
  selector: 'app-report',
  standalone: true,
  imports: [CommonModule, LoaderComponent, TextSliderComponent],
  templateUrl: './report.component.html',
  styleUrl: './report.component.css'
})
export class ReportComponent {
  selectedFile: File | null = null;
  isDragging = false;
  isProcessing = false;
  extractedText = '';
  summary: SummaryResponse | null = null;
  error = '';
  ocrConfidence: number = 0;
  currentStep: 'upload' | 'ocr' | 'summarizing' | 'complete' = 'upload';
  selectedMedicine: MedicineDetail | null = null;
  medicineAlternatives: string[] = [];
  isVoiceSpeaking = false;
  voiceError = '';
  speechLanguage: 'en' | 'ur' = 'ur';

  constructor(
    private apiService: ApiService,
    private voiceService: VoiceAssistantService
  ) {}

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.handleFile(file);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFile(files[0]);
    }
  }

  handleFile(file: File) {
    // Validate file type
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      this.error = 'Please upload a PDF or image file (PNG, JPG, JPEG)';
      return;
    }

    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
      this.error = 'File size must be less than 16MB';
      return;
    }

    this.selectedFile = file;
    this.error = '';
    this.processFile();
  }

  processFile() {
    if (!this.selectedFile) return;

    this.isProcessing = true;
    this.error = '';
    this.summary = null;
    this.extractedText = '';
    this.ocrConfidence = 0;
    this.currentStep = 'ocr';

    // Step 1: Extract text with OCR
    this.apiService.extractText(this.selectedFile).subscribe({
      next: (response) => {
        if (response.success) {
          this.extractedText = response.extracted_text;
          this.ocrConfidence = response.confidence;
          console.log(`OCR completed. Confidence: ${(response.confidence * 100).toFixed(2)}%`);
          console.log(`Extracted text length: ${this.extractedText.length} characters`);
          
          // Validate extracted text
          if (!this.extractedText || this.extractedText.trim().length < 10) {
            this.error = 'Could not extract enough text from the file. Please ensure the image is clear and readable.';
            this.isProcessing = false;
            this.currentStep = 'upload';
            return;
          }
          
          // Step 2: Summarize the extracted text
          this.currentStep = 'summarizing';
          this.summarizeText(this.selectedFile?.name || 'Medical Report');
        } else {
          this.error = 'Failed to extract text from the file. Please try again or use a different file.';
          this.isProcessing = false;
          this.currentStep = 'upload';
        }
      },
      error: (err) => {
        console.error('OCR Error:', err);
        
        // Extract error message from backend response
        let errorMessage = 'Error processing file. Please try again.';
        
        if (err.error && err.error.error) {
          // Backend returned an error message
          errorMessage = err.error.error;
        } else if (err.message) {
          errorMessage = err.message;
        }
        
        if (err.status === 0) {
          errorMessage = 'Cannot connect to the server. Please ensure the backend is running on http://localhost:5000';
        } else if (err.status === 400) {
          errorMessage = err.error?.error || 'Invalid file format. Please upload a PDF or image file (PNG, JPG, JPEG).';
        } else if (err.status === 413) {
          errorMessage = 'File is too large. Maximum size is 16MB.';
        } else if (err.status === 500) {
          // Show the actual backend error message
          errorMessage = err.error?.error || 'Server error occurred. Please check the backend logs.';
        }
        
        this.error = errorMessage;
        this.isProcessing = false;
        this.currentStep = 'upload';
      }
    });
  }

  summarizeText(reportTitle: string) {
    if (!this.extractedText) {
      this.error = 'No text available to summarize';
      this.isProcessing = false;
      this.currentStep = 'upload';
      return;
    }

    this.apiService.summarizeReport(this.extractedText, reportTitle).subscribe({
      next: (response) => {
        if (response.success) {
          this.summary = response;
          this.currentStep = 'complete';
          console.log('Summary generated successfully');
          console.log('Key findings:', response.key_findings?.length || 0);
          console.log('Medications:', response.medications?.length || 0);
          console.log('Warnings:', response.critical_warnings?.length || 0);
        } else {
          this.error = 'Failed to generate summary. The AI service may be unavailable.';
          this.currentStep = 'upload';
        }
        this.isProcessing = false;
      },
      error: (err) => {
        console.error('Summary Error:', err);
        if (err.status === 0) {
          this.error = 'Cannot connect to the server. Please ensure the backend is running.';
        } else if (err.status === 400) {
          this.error = 'Invalid request. The extracted text may be too short or invalid.';
        } else if (err.status === 500) {
          this.error = 'Server error. The AI service may be experiencing issues. Please try again later.';
        } else {
          this.error = `Error generating summary: ${err.message || 'Please try again.'}`;
        }
        this.isProcessing = false;
        this.currentStep = 'upload';
      }
    });
  }

  loadMedicineDetails(medicine: string) {
    this.apiService.getMedicineDetails(medicine).subscribe({
      next: (response) => {
        if (response.success) {
          this.selectedMedicine = response.medicine;
          this.medicineAlternatives = response.alternatives || [];
        }
      },
      error: () => {
        this.selectedMedicine = null;
        this.medicineAlternatives = [];
      }
    });
  }

  reset() {
    this.selectedFile = null;
    this.extractedText = '';
    this.summary = null;
    this.error = '';
    this.ocrConfidence = 0;
    this.currentStep = 'upload';
    this.selectedMedicine = null;
    this.medicineAlternatives = [];
    this.stopSummaryAudio();
    this.voiceError = '';
  }

  setSpeechLanguage(lang: 'en' | 'ur'): void {
    this.speechLanguage = lang;
  }

  async speakSummary(): Promise<void> {
    if (!this.summary) return;
    this.isVoiceSpeaking = true;
    this.voiceError = '';
    const textToSpeak = [
      `Patient summary: ${this.summary.patient_summary || ''}`,
      `Medical summary: ${this.summary.doctor_summary || ''}`,
      this.summary.follow_up ? `Follow up: ${this.summary.follow_up}` : '',
    ]
      .filter(Boolean)
      .join(' ');
    try {
      await this.voiceService.speak(textToSpeak, true, this.speechLanguage);
    } catch (error: any) {
      this.voiceError = error?.message || 'Unable to play voice summary. Please read the text.';
    } finally {
      this.isVoiceSpeaking = false;
    }
  }

  stopSummaryAudio(): void {
    this.voiceService.stopPlayback();
    this.isVoiceSpeaking = false;
  }

  getFileSize(size: number): string {
    if (size < 1024) return size + ' B';
    if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB';
    return (size / (1024 * 1024)).toFixed(2) + ' MB';
  }

  getFileType(file: File): string {
    if (file.type === 'application/pdf') return 'PDF';
    if (file.type.startsWith('image/')) return file.type.split('/')[1].toUpperCase();
    return 'Unknown';
  }

  getUrgencyClass(urgency: string): string {
    switch (urgency?.toLowerCase()) {
      case 'high': return 'badge-danger';
      case 'medium': return 'badge-warning';
      case 'low': return 'badge-success';
      default: return 'badge-info';
    }
  }
}
