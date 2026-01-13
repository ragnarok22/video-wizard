import { Composition } from 'remotion';
import { VideoComposition } from './compositions/VideoComposition';
import type { VideoCompositionProps } from './types';

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
        component={VideoComposition}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          videoUrl: '',
          subtitles: [],
          template: 'default',
          backgroundColor: '#000000',
        } as VideoCompositionProps}
      />
    </>
  );
};
