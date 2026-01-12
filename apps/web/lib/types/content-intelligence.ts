/**
 * Content Intelligence Module Types
 * 
 * Types for AI-powered transcript analysis and viral clip identification
 * Re-exports from server types for client usage
 */

// Re-export server types for client components
export type {
    AnalyzeContentErrorResponse, AnalyzeContentRequest,
    AnalyzeContentResponse, ContentAnalysis, ViralClip
} from '@/server/types/content-analysis';

/**
 * Transcript segment from Python processing engine
 */
export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  speaker?: string;
}

export interface FullTranscript {
  segments: TranscriptSegment[];
  duration: number;
  language?: string;
}
