/**
 * Aspect Ratio Constants & Utilities
 *
 * Shared definitions for multi-aspect ratio support across the entire pipeline.
 * Used by: frontend components, API routes, services, Remotion compositions.
 */

export type AspectRatio = '9:16' | '1:1' | '4:5' | '16:9';

export interface AspectRatioConfig {
  width: number;
  height: number;
  label: string;
  description: string;
  cssClass: string;
}

/**
 * Aspect ratio presets with dimensions, labels, and Tailwind classes
 */
export const ASPECT_RATIO_CONFIG: Record<AspectRatio, AspectRatioConfig> = {
  '9:16': {
    width: 1080,
    height: 1920,
    label: 'Vertical',
    description: 'TikTok, Reels, Stories',
    cssClass: 'aspect-[9/16]',
  },
  '1:1': {
    width: 1080,
    height: 1080,
    label: 'Square',
    description: 'Instagram Posts',
    cssClass: 'aspect-square',
  },
  '4:5': {
    width: 1080,
    height: 1350,
    label: 'Portrait',
    description: 'Instagram Feed',
    cssClass: 'aspect-[4/5]',
  },
  '16:9': {
    width: 1920,
    height: 1080,
    label: 'Landscape',
    description: 'YouTube, Standard',
    cssClass: 'aspect-video',
  },
};

export const DEFAULT_ASPECT_RATIO: AspectRatio = '9:16';

export const ASPECT_RATIO_OPTIONS: AspectRatio[] = ['9:16', '1:1', '4:5', '16:9'];

/**
 * Get dimensions for a given aspect ratio
 */
export function getDimensions(ratio: AspectRatio): { width: number; height: number } {
  const config = ASPECT_RATIO_CONFIG[ratio];
  return { width: config.width, height: config.height };
}

/**
 * Get Tailwind CSS class for a given aspect ratio
 */
export function getAspectClass(ratio: AspectRatio): string {
  return ASPECT_RATIO_CONFIG[ratio].cssClass;
}
