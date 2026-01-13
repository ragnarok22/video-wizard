import { AbsoluteFill, Html5Video, Sequence, useCurrentFrame, useVideoConfig } from 'remotion';
import type { VideoCompositionProps } from '../types';
import { CaptionOverlay } from './CaptionOverlay';

/**
 * Video Composition Component (Phase Q)
 * 
 * Main composition that renders:
 * 1. Video background layer (cropped MP4 from Python service)
 * 2. Caption overlay layer (synchronized subtitles)
 */
export function VideoComposition({
  videoUrl,
  subtitles,
  template,
  backgroundColor = '#000000',
}: VideoCompositionProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Calculate current time in seconds
  const currentTime = frame / fps;

  return (
    <AbsoluteFill style={{ backgroundColor }}>
      {/* Layer 1: Video Background */}
      <Sequence from={0}>
        <AbsoluteFill>
          <Html5Video
            src={videoUrl}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
        </AbsoluteFill>
      </Sequence>

      {/* Layer 2: Caption Overlay */}
      <Sequence from={0}>
        <CaptionOverlay
          subtitles={subtitles}
          currentTime={currentTime}
          template={template}
        />
      </Sequence>
    </AbsoluteFill>
  );
}
