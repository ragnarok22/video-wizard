import { Composition } from 'remotion';
import { VideoComposition } from './compositions/VideoComposition';
import type { VideoCompositionProps } from './types';

/**
 * Aspect ratio dimension map for calculating composition width/height
 */
const ASPECT_DIMENSIONS: Record<string, { width: number; height: number }> = {
  '9:16': { width: 1080, height: 1920 },
  '1:1': { width: 1080, height: 1080 },
  '4:5': { width: 1080, height: 1350 },
  '16:9': { width: 1920, height: 1080 },
};

/**
 * Remotion Root Component
 *
 * Registers all video compositions available for rendering
 * Each composition defines a timeline with video + subtitles
 */
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="VideoWithSubtitles"
        component={VideoComposition as unknown as React.ComponentType<Record<string, unknown>>}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={({ props }) => {
          const { aspectRatio, durationInFrames } = props as unknown as VideoCompositionProps & {
            aspectRatio?: string;
            durationInFrames?: number;
          };
          const dims = aspectRatio ? ASPECT_DIMENSIONS[aspectRatio] : undefined;
          const dimensionOverrides = dims ? { width: dims.width, height: dims.height } : {};

          if (durationInFrames) {
            return { durationInFrames, ...dimensionOverrides };
          }

          return { durationInFrames: 300, ...dimensionOverrides };
        }}
        defaultProps={
          {
            videoUrl: '',
            subtitles: [],
            template: 'default',
            backgroundColor: '#000000',
          } as VideoCompositionProps
        }
      />
    </>
  );
};
