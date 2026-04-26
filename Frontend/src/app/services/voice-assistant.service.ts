import { Injectable } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class VoiceAssistantService {
  private mediaRecorder: MediaRecorder | null = null;
  private stream: MediaStream | null = null;
  private chunks: BlobPart[] = [];
  private activeAudio: HTMLAudioElement | null = null;
  private activeUtterance: SpeechSynthesisUtterance | null = null;
  private readonly mimeType = 'audio/webm';
  private readonly disclaimers: Record<string, string> = {
    en: 'This is an AI-generated summary for educational purposes only. Always consult a licensed medical professional for medical decisions.',
    ur: 'یہ صرف معلوماتی مقصد کے لیے AI کا تیار کردہ خلاصہ ہے۔ کسی بھی طبی فیصلے سے پہلے ڈاکٹر سے ضرور رجوع کریں۔',
    hi: 'यह केवल जानकारी के लिए AI द्वारा तैयार सारांश है। चिकित्सा निर्णय के लिए हमेशा लाइसेंस प्राप्त चिकित्सक से सलाह लें।'
  };
  private readonly browserLangMap: Record<string, string> = {
    en: 'en-US',
    ur: 'ur-PK',
    hi: 'hi-IN',
    ar: 'ar-SA',
    es: 'es-ES',
    fr: 'fr-FR'
  };

  constructor(private apiService: ApiService) {}

  async startRecording(): Promise<void> {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error('Microphone is not supported in this browser');
    }
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      return;
    }

    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.chunks = [];
    this.mediaRecorder = new MediaRecorder(this.stream, { mimeType: this.mimeType });
    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        this.chunks.push(event.data);
      }
    };
    this.mediaRecorder.start();
  }

  async stopRecording(): Promise<Blob> {
    if (!this.mediaRecorder || this.mediaRecorder.state !== 'recording') {
      throw new Error('Recording is not active');
    }

    const recorder = this.mediaRecorder;
    const blob = await new Promise<Blob>((resolve) => {
      recorder.onstop = () => {
        const audioBlob = new Blob(this.chunks, { type: this.mimeType });
        resolve(audioBlob);
      };
      recorder.stop();
    });

    this.stopTracks();
    this.mediaRecorder = null;
    this.chunks = [];
    return blob;
  }

  async transcribeAudio(blob: Blob): Promise<string> {
    const response = await firstValueFrom(this.apiService.transcribeVoice(blob, 'voice.webm'));
    if (!response.success || !response.transcript?.trim()) {
      throw new Error(response.error || 'Transcription failed');
    }
    return response.transcript.trim();
  }

  async speak(
    text: string,
    includeDisclaimer: boolean = true,
    language: string = 'en'
  ): Promise<void> {
    const cleanText = (text || '').trim();
    if (!cleanText) {
      throw new Error('Nothing to read aloud');
    }
    const lang = (language || 'en').toLowerCase();

    let textForBrowser = cleanText;
    let translatedFromBackend = false;
    try {
      const response = await firstValueFrom(
        this.apiService.synthesizeVoice(text, includeDisclaimer, lang)
      );
      if (response?.text_used) {
        textForBrowser = response.text_used;
        translatedFromBackend = true;
      }
      if (response?.success && response.audio_base64 && response.mime_type) {
        await this.playAudio(response.audio_base64, response.mime_type);
        return;
      }
      console.warn('Cloud TTS unavailable, falling back to browser voice.', response?.error);
    } catch (cloudError: any) {
      const errBody = cloudError?.error;
      if (errBody?.text_used) {
        textForBrowser = errBody.text_used;
        translatedFromBackend = true;
      }
      console.warn('Cloud TTS failed, falling back to browser voice.', cloudError);
    }

    if (!translatedFromBackend && includeDisclaimer) {
      const disclaimer = this.disclaimers[lang] || this.disclaimers['en'];
      textForBrowser = `${cleanText}\n\n${disclaimer}`;
    }
    await this.speakWithBrowser(textForBrowser, lang);
  }

  stopPlayback(): void {
    if (this.activeAudio) {
      this.activeAudio.pause();
      this.activeAudio.currentTime = 0;
      this.activeAudio = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch {
        /* no-op */
      }
    }
    this.activeUtterance = null;
  }

  private speakWithBrowser(text: string, language: string = 'en'): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
        reject(new Error('Browser speech synthesis is not supported'));
        return;
      }
      const ttsLang = (this.browserLangMap[language] || language || 'en-US');
      const synth = window.speechSynthesis;

      const startSpeaking = (voices: SpeechSynthesisVoice[]) => {
        try {
          synth.cancel();
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.lang = ttsLang;
          utterance.rate = language === 'ur' ? 0.9 : 1.0;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;

          const langPrefix = ttsLang.split(/[-_]/)[0].toLowerCase();
          const voiceNamePattern: Record<string, RegExp> = {
            ur: /urdu|asad|uzma/i,
            hi: /hindi|hemant|kalpana|swara/i,
            ar: /arabic|hoda|naayf/i
          };

          let voice =
            voices.find(
              (v) => v.lang && v.lang.toLowerCase() === ttsLang.toLowerCase()
            ) ||
            voices.find(
              (v) => v.lang && v.lang.toLowerCase().startsWith(langPrefix + '-')
            ) ||
            voices.find(
              (v) => v.lang && v.lang.toLowerCase() === langPrefix
            );

          const namePattern = voiceNamePattern[language];
          if (!voice && namePattern) {
            voice = voices.find((v) => namePattern.test(v.name));
          }
          if (!voice && language === 'en') {
            voice = voices.find(
              (v) =>
                /en[-_](US|GB)/i.test(v.lang) &&
                /female|google|samantha|aria|jenny|natural/i.test(v.name)
            );
          }
          if (voice) {
            utterance.voice = voice;
            console.log(
              `[voice] selected="${voice.name}" lang="${voice.lang}" requested="${ttsLang}"`
            );
          } else {
            console.warn(
              `[voice] no matching voice for lang="${ttsLang}". Available:`,
              voices.map((v) => `${v.name} (${v.lang})`).join(', ')
            );
          }

          this.activeUtterance = utterance;
          utterance.onend = () => {
            this.activeUtterance = null;
            resolve();
          };
          utterance.onerror = (event) => {
            this.activeUtterance = null;
            reject(new Error(event.error || 'Speech synthesis failed'));
          };
          synth.speak(utterance);
        } catch (err) {
          reject(err instanceof Error ? err : new Error(String(err)));
        }
      };

      const initialVoices = synth.getVoices();
      if (initialVoices && initialVoices.length > 0) {
        startSpeaking(initialVoices);
        return;
      }
      // Voices load async on first call in some browsers
      const handleVoicesChanged = () => {
        synth.onvoiceschanged = null;
        startSpeaking(synth.getVoices());
      };
      synth.onvoiceschanged = handleVoicesChanged;
      // Fallback: start after a short delay even if no voices loaded
      setTimeout(() => {
        if (this.activeUtterance) return;
        startSpeaking(synth.getVoices());
      }, 400);
    });
  }

  private async playAudio(audioBase64: string, mimeType: string): Promise<void> {
    this.stopPlayback();
    const src = `data:${mimeType};base64,${audioBase64}`;
    const audio = new Audio(src);
    this.activeAudio = audio;
    await new Promise<void>((resolve, reject) => {
      audio.onended = () => resolve();
      audio.onerror = () => reject(new Error('Unable to play generated audio'));
      audio.play().catch(reject);
    });
  }

  private stopTracks(): void {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
  }
}
