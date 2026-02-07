/**
 * Remotion Configuration
 *
 * Configure Remotion behavior for rendering and preview
 */

export const REMOTION_CONFIG = {
  // Default composition settings
  DEFAULT_FPS: 30,
  DEFAULT_WIDTH: 1080,
  DEFAULT_HEIGHT: 1920, // 9:16 aspect ratio for vertical video

  // Rendering settings
  VIDEO_CODEC: 'h264' as const,
  AUDIO_CODEC: 'aac' as const,

  // Quality settings
  VIDEO_BITRATE: '4M',
  AUDIO_BITRATE: '192k',

  // Export settings (used with @remotion/renderer)
  OVERWRITE_OUTPUT: true,
  GIF_LOOPS: 0,
} as const;

/**
 * Aspect ratio dimension presets for Remotion compositions
 */
export const ASPECT_RATIO_DIMENSIONS: Record<string, { width: number; height: number }> = {
  '9:16': { width: 1080, height: 1920 },
  '1:1': { width: 1080, height: 1080 },
  '4:5': { width: 1080, height: 1350 },
  '16:9': { width: 1920, height: 1080 },
};
