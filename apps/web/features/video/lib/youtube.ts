/**
 * YouTube URL Validation Utilities
 *
 * Validates and extracts video IDs from YouTube URLs.
 * Supports standard watch URLs, short URLs, and Shorts URLs.
 */

const YOUTUBE_PATTERNS = [
  // https://www.youtube.com/watch?v=VIDEO_ID
  /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})/,
  // https://youtu.be/VIDEO_ID
  /(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})/,
  // https://www.youtube.com/shorts/VIDEO_ID
  /(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/,
  // https://www.youtube.com/embed/VIDEO_ID
  /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
  // https://www.youtube.com/v/VIDEO_ID
  /(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})/,
];

/**
 * Checks if a string is a valid YouTube URL
 */
export function isYouTubeUrl(url: string): boolean {
  const trimmed = url.trim();
  if (!trimmed) return false;
  return YOUTUBE_PATTERNS.some((pattern) => pattern.test(trimmed));
}

/**
 * Extracts the video ID from a YouTube URL
 * Returns null if the URL is not a valid YouTube URL
 */
export function extractVideoId(url: string): string | null {
  const trimmed = url.trim();
  for (const pattern of YOUTUBE_PATTERNS) {
    const match = trimmed.match(pattern);
    if (match?.[1]) {
      return match[1];
    }
  }
  return null;
}
