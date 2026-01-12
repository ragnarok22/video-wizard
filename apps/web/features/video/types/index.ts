/**
 * Video Feature Types
 * 
 * Type definitions for the video processing feature
 */

export interface TranscriptSegment {
  id: number;
  start: number;
  end: number;
  text: string;
}

export interface TranscriptionResult {
  video_path: string;
  audio_path?: string;
  segments: TranscriptSegment[];
  full_text: string;
  segment_count: number;
}

export type ProcessingStep = 
  | 'idle' 
  | 'uploading' 
  | 'transcribing' 
  | 'analyzing' 
  | 'complete' 
  | 'error';

export type StepStatus = 'complete' | 'current' | 'error' | 'pending';

export interface VideoProcessingState {
  file: File | null;
  currentStep: ProcessingStep;
  uploadedPath: string;
  transcription: TranscriptionResult | null;
  analysis: any | null;
  error: string;
  progress: string;
}
