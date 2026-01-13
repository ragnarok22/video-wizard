import type { SubtitleSegment } from '../types';

/**
 * Subtitle Utilities (Phase R)
 * 
 * Helper functions for subtitle timing and synchronization
 */

/**
 * Convert frame number to time in seconds
 */
export function frameToTime(frame: number, fps: number): number {
  return frame / fps;
}

/**
 * Convert time in seconds to frame number
 */
export function timeToFrame(time: number, fps: number): number {
  return Math.floor(time * fps);
}

/**
 * Calculate total duration in frames from subtitle segments
 */
export function calculateDurationFromSubtitles(
  subtitles: SubtitleSegment[],
  fps: number
): number {
  if (subtitles.length === 0) return 0;
  
  const lastSegment = subtitles[subtitles.length - 1];
  return timeToFrame(lastSegment.end, fps);
}

/**
 * Find segment at specific time
 */
export function findSegmentAtTime(
  subtitles: SubtitleSegment[],
  time: number
): SubtitleSegment | null {
  return subtitles.find((segment) => time >= segment.start && time < segment.end) ?? null;
}

/**
 * Get segments within a time range
 */
export function getSegmentsInRange(
  subtitles: SubtitleSegment[],
  startTime: number,
  endTime: number
): SubtitleSegment[] {
  return subtitles.filter(
    (segment) =>
      (segment.start >= startTime && segment.start < endTime) ||
      (segment.end > startTime && segment.end <= endTime) ||
      (segment.start < startTime && segment.end > endTime)
  );
}

/**
 * Validate subtitle timing integrity
 */
export function validateSubtitleTiming(subtitles: SubtitleSegment[]): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  for (let i = 0; i < subtitles.length; i++) {
    const segment = subtitles[i];

    // Check if start < end
    if (segment.start >= segment.end) {
      errors.push(`Segment ${segment.id}: start time must be less than end time`);
    }

    // Check if segments overlap
    if (i > 0) {
      const prevSegment = subtitles[i - 1];
      if (segment.start < prevSegment.end) {
        errors.push(`Segment ${segment.id} overlaps with segment ${prevSegment.id}`);
      }
    }

    // Validate word timing if present
    if (segment.words) {
      for (const word of segment.words) {
        if (word.start < segment.start || word.end > segment.end) {
          errors.push(
            `Word "${word.word}" timing outside segment ${segment.id} boundaries`
          );
        }
      }
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}
