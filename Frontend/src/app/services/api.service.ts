import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface OCRResponse {
  success: boolean;
  extracted_text: string;
  confidence: number;
}

export interface SummaryResponse {
  success: boolean;
  patient_summary: string;
  doctor_summary: string;
  key_findings: string[];
  medications?: string[];
  medicine_details?: MedicineDetail[];
  critical_warnings?: string[];
  follow_up?: string;
  saved_report_id?: number;
}

export interface SymptomResponse {
  success: boolean;
  possible_conditions: Array<{
    name: string;
    probability: string;
    description: string;
  }>;
  urgency: string;
  explanation: string;
  recommendations: string[];
  context_sources?: string[];
  citations?: string[];
  seek_immediate_care_if?: string[];
}

export interface AuthResponse {
  success: boolean;
  user_id: number;
  email: string;
  token: string;
}

export interface ReportListItem {
  id: number;
  report_title: string;
  created_at: string;
}

export interface MedicineDetail {
  name: string;
  generic_name: string;
  ingredients: string[];
  uses: string[];
  alternatives: string[];
  source: string;
}

export interface VoiceTranscriptionResponse {
  success: boolean;
  transcript: string;
  error?: string;
}

export interface VoiceSynthesisResponse {
  success: boolean;
  audio_base64?: string;
  mime_type?: string;
  text_used?: string;
  language?: string;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;
  private readonly tokenKey = 'medisense_token';

  constructor(private http: HttpClient) { }

  private authHeaders(): HttpHeaders {
    const token = this.getToken();
    if (!token) return new HttpHeaders();
    return new HttpHeaders({ Authorization: `Bearer ${token}` });
  }

  getToken(): string {
    return localStorage.getItem(this.tokenKey) || '';
  }

  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  clearToken(): void {
    localStorage.removeItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  register(email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/register`, { email, password });
  }

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login`, { email, password });
  }

  // OCR Text Extraction
  extractText(file: File): Observable<OCRResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<OCRResponse>(`${this.apiUrl}/ocr`, formData);
  }

  // Report Summarization
  summarizeReport(text: string, reportTitle: string): Observable<SummaryResponse> {
    return this.http.post<SummaryResponse>(
      `${this.apiUrl}/summarize`,
      { text, report_title: reportTitle },
      { headers: this.authHeaders() }
    );
  }

  // Symptom Analysis
  checkSymptoms(symptoms: string): Observable<SymptomResponse> {
    return this.http.post<SymptomResponse>(
      `${this.apiUrl}/symptom-check`,
      { symptoms },
      { headers: this.authHeaders() }
    );
  }

  listReports(): Observable<{ success: boolean; reports: ReportListItem[] }> {
    return this.http.get<{ success: boolean; reports: ReportListItem[] }>(`${this.apiUrl}/reports`, {
      headers: this.authHeaders(),
    });
  }

  getReport(reportId: number): Observable<{ success: boolean; report: any }> {
    return this.http.get<{ success: boolean; report: any }>(`${this.apiUrl}/reports/${reportId}`, {
      headers: this.authHeaders(),
    });
  }

  getMedicineDetails(name: string): Observable<{ success: boolean; medicine: MedicineDetail; alternatives: string[] }> {
    return this.http.get<{ success: boolean; medicine: MedicineDetail; alternatives: string[] }>(
      `${this.apiUrl}/medicines/${encodeURIComponent(name)}`,
      { headers: this.authHeaders() }
    );
  }

  createOrResumeThread(reportId?: number): Observable<{ success: boolean; thread: { id: number } }> {
    return this.http.post<{ success: boolean; thread: { id: number } }>(
      `${this.apiUrl}/chat/thread`,
      { report_id: reportId },
      { headers: this.authHeaders() }
    );
  }

  getThreadMessages(threadId: number): Observable<{ success: boolean; messages: any[] }> {
    return this.http.get<{ success: boolean; messages: any[] }>(
      `${this.apiUrl}/chat/thread/${threadId}/messages`,
      { headers: this.authHeaders() }
    );
  }

  askFollowup(threadId: number, question: string): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/chat/thread/${threadId}/ask`,
      { question },
      { headers: this.authHeaders() }
    );
  }

  transcribeVoice(audio: Blob, filename: string = 'voice.webm'): Observable<VoiceTranscriptionResponse> {
    const formData = new FormData();
    formData.append('audio', audio, filename);
    return this.http.post<VoiceTranscriptionResponse>(`${this.apiUrl}/voice/transcribe`, formData, {
      headers: this.authHeaders()
    });
  }

  synthesizeVoice(
    text: string,
    includeDisclaimer: boolean = true,
    language: string = 'en'
  ): Observable<VoiceSynthesisResponse> {
    return this.http.post<VoiceSynthesisResponse>(
      `${this.apiUrl}/voice/speak`,
      {
        text,
        include_disclaimer: includeDisclaimer,
        language
      },
      {
        headers: this.authHeaders()
      }
    );
  }
}
