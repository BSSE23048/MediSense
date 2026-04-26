import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, SymptomResponse } from '../../services/api.service';
import { VoiceAssistantService } from '../../services/voice-assistant.service';
import { LoaderComponent } from '../../components/loader/loader.component';
import { TextSliderComponent } from '../../components/text-slider/text-slider.component';

@Component({
  selector: 'app-symptoms',
  standalone: true,
  imports: [CommonModule, FormsModule, LoaderComponent, TextSliderComponent],
  templateUrl: './symptoms.component.html',
  styleUrl: './symptoms.component.css'
})
export class SymptomsComponent {
  symptoms = '';
  isAnalyzing = false;
  analysis: SymptomResponse | null = null;
  error = '';
  followupQuestion = '';
  chatThreadId: number | null = null;
  chatMessages: Array<{ role: string; message: string; sources?: string[] }> = [];
  isVoiceRecording = false;
  isVoiceTranscribing = false;
  isVoiceSpeaking = false;
  voiceError = '';

  constructor(
    private apiService: ApiService,
    private voiceService: VoiceAssistantService
  ) {}

  analyzeSymptoms() {
    if (!this.symptoms.trim()) {
      this.error = 'Please describe your symptoms';
      return;
    }

    this.isAnalyzing = true;
    this.error = '';
    this.analysis = null;

    this.apiService.checkSymptoms(this.symptoms).subscribe({
      next: (response) => {
        if (response.success) {
          this.analysis = response;
          this.ensureThread();
        } else {
          this.error = 'Failed to analyze symptoms';
        }
        this.isAnalyzing = false;
      },
      error: (err) => {
        this.error = 'Error analyzing symptoms. Please try again.';
        this.isAnalyzing = false;
        console.error('Symptom Analysis Error:', err);
      }
    });
  }

  ensureThread() {
    if (!this.apiService.isLoggedIn()) {
      return;
    }
    this.apiService.createOrResumeThread().subscribe({
      next: (response) => {
        if (response.success) {
          this.chatThreadId = response.thread.id;
          this.loadThreadHistory();
        }
      }
    });
  }

  loadThreadHistory() {
    if (!this.chatThreadId) return;
    this.apiService.getThreadMessages(this.chatThreadId).subscribe({
      next: (response) => {
        if (response.success) {
          this.chatMessages = response.messages.map((message) => ({
            role: message.role,
            message: message.message,
            sources: message.sources || []
          }));
        }
      }
    });
  }

  askFollowup() {
    if (!this.chatThreadId || !this.followupQuestion.trim()) return;
    const question = this.followupQuestion.trim();
    this.chatMessages.push({ role: 'user', message: question });
    this.followupQuestion = '';
    this.apiService.askFollowup(this.chatThreadId, question).subscribe({
      next: (response) => {
        const assistantMessage = response.answer || 'No response generated.';
        this.chatMessages.push({
          role: 'assistant',
          message: assistantMessage,
          sources: response.sources || []
        });
        this.speakAssistantMessage(assistantMessage);
      },
      error: () => {
        this.chatMessages.push({
          role: 'assistant',
          message: 'Unable to process follow-up right now. Please try again.'
        });
      }
    });
  }

  reset() {
    this.symptoms = '';
    this.analysis = null;
    this.error = '';
    this.followupQuestion = '';
    this.chatMessages = [];
    this.chatThreadId = null;
    this.stopSpeaking();
    this.voiceError = '';
  }

  async startVoiceInput(target: 'symptoms' | 'followup'): Promise<void> {
    this.voiceError = '';
    try {
      await this.voiceService.startRecording();
      this.isVoiceRecording = true;
      if (target === 'symptoms') {
        this.error = '';
      }
    } catch (error: any) {
      this.voiceError = error?.message || 'Unable to access microphone.';
    }
  }

  async stopVoiceInput(target: 'symptoms' | 'followup'): Promise<void> {
    if (!this.isVoiceRecording) return;
    this.isVoiceRecording = false;
    this.isVoiceTranscribing = true;
    this.voiceError = '';
    try {
      const audioBlob = await this.voiceService.stopRecording();
      const transcript = await this.voiceService.transcribeAudio(audioBlob);
      if (target === 'symptoms') {
        this.symptoms = this.appendTranscript(this.symptoms, transcript);
      } else {
        this.followupQuestion = this.appendTranscript(this.followupQuestion, transcript);
      }
    } catch (error: any) {
      this.voiceError = error?.message || 'Voice transcription failed.';
    } finally {
      this.isVoiceTranscribing = false;
    }
  }

  async speakAssistantMessage(text: string): Promise<void> {
    if (!text?.trim()) return;
    this.voiceError = '';
    this.isVoiceSpeaking = true;
    try {
      await this.voiceService.speak(text, true);
    } catch (error: any) {
      this.voiceError = error?.message || 'Voice playback unavailable. Please read the text response.';
    } finally {
      this.isVoiceSpeaking = false;
    }
  }

  stopSpeaking(): void {
    this.voiceService.stopPlayback();
    this.isVoiceSpeaking = false;
  }

  private appendTranscript(existing: string, transcript: string): string {
    if (!existing.trim()) return transcript;
    return `${existing.trim()} ${transcript}`.trim();
  }

  getUrgencyClass(urgency: string): string {
    switch (urgency?.toLowerCase()) {
      case 'high': return 'badge-danger';
      case 'medium': return 'badge-warning';
      case 'low': return 'badge-success';
      default: return 'badge-info';
    }
  }

  getProbabilityClass(probability: string): string {
    switch (probability?.toLowerCase()) {
      case 'high': return 'probability-high';
      case 'medium': return 'probability-medium';
      case 'low': return 'probability-low';
      default: return '';
    }
  }
}
