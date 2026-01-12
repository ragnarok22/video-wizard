/**
 * Utility functions for Content Intelligence Module
 */

/**
 * Format seconds to MM:SS format
 */
export function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format seconds to human-readable duration (e.g., "1m 30s")
 */
export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  
  if (mins === 0) {
    return `${secs}s`;
  }
  
  if (secs === 0) {
    return `${mins}m`;
  }
  
  return `${mins}m ${secs}s`;
}

/**
 * Get color class for viral score
 */
export function getViralScoreColor(score: number): string {
  if (score >= 90) return 'bg-green-500';
  if (score >= 70) return 'bg-blue-500';
  if (score >= 50) return 'bg-yellow-500';
  if (score >= 30) return 'bg-orange-500';
  return 'bg-red-500';
}

/**
 * Get label for viral score
 */
export function getViralScoreLabel(score: number): string {
  if (score >= 90) return 'Extremely Viral';
  if (score >= 70) return 'High Potential';
  if (score >= 50) return 'Good Potential';
  if (score >= 30) return 'Moderate';
  return 'Low Potential';
}

/**
 * Calculate average viral score from clips
 */
export function calculateAverageScore(clips: Array<{ viral_score: number }>): number {
  if (clips.length === 0) return 0;
  const sum = clips.reduce((acc, clip) => acc + clip.viral_score, 0);
  return Math.round((sum / clips.length) * 10) / 10;
}

/**
 * Parse timestamp string (e.g., "[00:15 - 00:45]") to seconds
 */
export function parseTimestampRange(timestamp: string): { start: number; end: number } | null {
  const match = timestamp.match(/\[(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})\]/);
  
  if (!match) return null;
  
  const [, startMin, startSec, endMin, endSec] = match;
  
  return {
    start: parseInt(startMin) * 60 + parseInt(startSec),
    end: parseInt(endMin) * 60 + parseInt(endSec),
  };
}

/**
 * Convert transcript segments to formatted string
 */
export function formatTranscriptSegments(
  segments: Array<{ start: number; end: number; text: string }>
): string {
  return segments
    .map(segment => {
      const start = formatTimestamp(segment.start);
      const end = formatTimestamp(segment.end);
      return `[${start} - ${end}] ${segment.text}`;
    })
    .join('\n\n');
}

/**
 * Validate clip duration is within acceptable range (30-90 seconds)
 */
export function isValidClipDuration(startTime: number, endTime: number): boolean {
  const duration = endTime - startTime;
  return duration >= 30 && duration <= 90;
}

/**
 * Group clips by viral score tier
 */
export function groupClipsByTier(clips: Array<{ viral_score: number }>) {
  return {
    extremelyViral: clips.filter(c => c.viral_score >= 90),
    highPotential: clips.filter(c => c.viral_score >= 70 && c.viral_score < 90),
    goodPotential: clips.filter(c => c.viral_score >= 50 && c.viral_score < 70),
    moderate: clips.filter(c => c.viral_score >= 30 && c.viral_score < 50),
    low: clips.filter(c => c.viral_score < 30),
  };
}
