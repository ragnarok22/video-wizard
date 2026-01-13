# Subtitle & Composition Engine - Implementation Guide

## Overview

The Subtitle & Composition Engine handles visual assembly of final videos by overlaying synchronized subtitles on cropped video clips using Remotion within Next.js.

## Architecture

### Directory Structure

```
apps/web/
├── remotion/                           # Remotion compositions
│   ├── index.ts                       # Entry point
│   ├── Root.tsx                       # Composition registration
│   ├── config.ts                      # Remotion configuration
│   ├── types.ts                       # TypeScript types
│   ├── compositions/                  # Video compositions
│   │   ├── VideoComposition.tsx       # Main composition
│   │   └── CaptionOverlay.tsx         # Caption layer
│   ├── templates/                     # Caption templates (Phase S)
│   │   ├── DefaultTemplate.tsx        # Simple bottom captions
│   │   ├── ViralTemplate.tsx          # High-impact center captions
│   │   ├── MinimalTemplate.tsx        # Ultra-clean captions
│   │   └── ModernTemplate.tsx         # Gradient accent captions
│   ├── hooks/                         # Custom hooks
│   │   └── useActiveSubtitle.ts       # Subtitle synchronization
│   └── utils/                         # Utility functions
│       └── subtitle-utils.ts          # Timing calculations
├── components/
│   └── video-editor/                  # Editor UI components
│       ├── VideoEditorPreview.tsx     # Player with template selector
│       └── ExportControls.tsx         # Export button & progress
├── features/
│   └── video/
│       └── containers/
│           └── editor-container.tsx   # Editor page container
├── app/
│   ├── editor/[id]/                   # Editor page
│   │   └── page.tsx                   # Main editor route
│   └── api/
│       └── render-final/              # Server-side rendering
│           └── route.ts               # POST endpoint
└── server/
    ├── services/
    │   └── video-render-service.ts    # Rendering logic
    └── types/
        └── video-render.ts            # Zod schemas
```

## Implementation Details

### Phase P: Remotion Setup ✅

**Files Created:**
- `remotion/index.ts` - Entry point for Remotion CLI
- `remotion/Root.tsx` - Registers compositions
- `remotion/config.ts` - Configuration settings
- `remotion/types.ts` - TypeScript interfaces

**Key Configuration:**
```typescript
const REMOTION_CONFIG = {
  DEFAULT_FPS: 30,
  DEFAULT_WIDTH: 1080,
  DEFAULT_HEIGHT: 1920,  // 9:16 aspect ratio
  VIDEO_CODEC: 'h264',
  AUDIO_CODEC: 'aac',
};
```

### Phase Q: Composition Component ✅

**Files Created:**
- `remotion/compositions/VideoComposition.tsx`
- `remotion/compositions/CaptionOverlay.tsx`

**Architecture:**
```
VideoComposition
├── Layer 1: Video Background (Sequence)
│   └── Video element (MP4 from Python service)
└── Layer 2: Caption Overlay (Sequence)
    └── Dynamic caption template
```

**Key Features:**
- Two-layer composition system
- Video fills entire frame (9:16)
- Captions rendered as transparent overlay
- Template selection via props

### Phase R: Subtitle Synchronization ✅

**Files Created:**
- `remotion/hooks/useActiveSubtitle.ts`
- `remotion/utils/subtitle-utils.ts`

**Synchronization Logic:**
```typescript
// 1. Get current time from frame
const currentTime = frame / fps;

// 2. Find active segment
const currentSegment = subtitles.find(
  seg => currentTime >= seg.start && currentTime < seg.end
);

// 3. Find active word (if word-level timing exists)
const activeWord = currentSegment.words.find(
  word => currentTime >= word.start && currentTime < word.end
);
```

**Utilities:**
- `frameToTime()` - Convert frame number to seconds
- `timeToFrame()` - Convert seconds to frame number
- `calculateDurationFromSubtitles()` - Get total duration
- `findSegmentAtTime()` - Find subtitle at specific time
- `validateSubtitleTiming()` - Check timing integrity

### Phase S: Template System ✅

**Files Created:**
- `remotion/templates/DefaultTemplate.tsx`
- `remotion/templates/ViralTemplate.tsx`
- `remotion/templates/MinimalTemplate.tsx`
- `remotion/templates/ModernTemplate.tsx`

**Templates Overview:**

| Template | Style | Animation | Use Case |
|----------|-------|-----------|----------|
| **Default** | Bottom text, black bg | Subtle fade | General purpose |
| **Viral** | Large center, yellow bg | Bouncy scale | High-impact shorts |
| **Minimal** | Clean bottom text | Gentle fade | Professional content |
| **Modern** | Gradient accent | Slide up | Contemporary look |

**Template Props:**
```typescript
interface CaptionTemplateProps {
  currentWord: string;
  currentSegment: SubtitleSegment | null;
  isActive: boolean;
}
```

### Phase T: Preview & Export ✅

#### Browser Preview

**Files Created:**
- `components/video-editor/VideoEditorPreview.tsx`
- `components/video-editor/ExportControls.tsx`

**Features:**
- Real-time Remotion Player
- Template selector buttons
- Play/pause controls
- Loop functionality
- Responsive sizing

**Usage:**
```tsx
<VideoEditorPreview
  videoUrl="http://localhost:8000/output/clip.mp4"
  subtitles={subtitleData}
  initialTemplate="default"
  onTemplateChange={(template) => console.log(template)}
/>
```

#### Server-Side Rendering

**Files Created:**
- `server/services/video-render-service.ts`
- `server/types/video-render.ts`
- `app/api/render-final/route.ts`

**Rendering Process:**
1. Bundle Remotion composition
2. Select composition with props
3. Render frames using headless browser
4. Stitch frames into MP4 with FFmpeg
5. Return download URL

**API Endpoint:**
```typescript
POST /api/render-final
Content-Type: application/json

{
  "videoUrl": "http://localhost:8000/output/clip.mp4",
  "subtitles": [...],
  "template": "viral",
  "outputFormat": "mp4",
  "quality": "high"
}
```

**Response:**
```json
{
  "success": true,
  "outputUrl": "/rendered/video_abc123.mp4",
  "outputPath": "/path/to/file.mp4",
  "fileSize": 5242880,
  "duration": 30.5
}
```

#### Editor Page

**Files Created:**
- `features/video/containers/editor-container.tsx`
- `app/editor/[id]/page.tsx`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│  Preview Section (2/3 width)                    │
│  - Template selector buttons                     │
│  - Remotion Player with video + captions        │
└─────────────────────────────────────────────────┘
┌─────────────────────┐
│  Export Section     │
│  (1/3 width)        │
│  - Export button    │
│  - Progress bar     │
│  - Video info       │
└─────────────────────┘
```

## Usage Examples

### 1. Basic Preview

```typescript
import { VideoEditorContainer } from '@/features/video/containers/editor-container';

export default function Page() {
  return (
    <VideoEditorContainer
      videoUrl="http://localhost:8000/output/clip.mp4"
      subtitles={subtitleData}
    />
  );
}
```

### 2. Custom Template

```typescript
import { VideoComposition } from '@/remotion/compositions/VideoComposition';

const props = {
  videoUrl: 'video.mp4',
  subtitles: [...],
  template: 'viral',
  backgroundColor: '#000000',
};
```

### 3. Server-Side Rendering

```typescript
import { videoRenderService } from '@/server/services/video-render-service';

const result = await videoRenderService.renderVideo({
  videoUrl: 'video.mp4',
  subtitles: [...],
  template: 'modern',
  outputFormat: 'mp4',
  quality: 'high',
});
```

## Integration Workflow

### Complete Pipeline

1. **Upload Video** → Python service (`/upload`)
2. **Transcribe** → Python service (`/transcribe`)
3. **Create Clip** → Python service (`/render-clip`)
4. **Preview with Subtitles** → Next.js editor page
5. **Export Final Video** → Remotion rendering (`/api/render-final`)
6. **Download** → User gets final MP4

### Example Code

```typescript
// Step 1: Create clip from Python service
const clipResponse = await fetch('http://localhost:8000/render-clip', {
  method: 'POST',
  body: JSON.stringify({
    video_path: 'uploads/video.mp4',
    start_time: 10,
    end_time: 40,
    crop_mode: 'dynamic',
  }),
});
const { output_url } = await clipResponse.json();

// Step 2: Get transcription
const transcriptResponse = await fetch('http://localhost:8000/transcribe', {
  method: 'POST',
  body: JSON.stringify({ video_path: 'uploads/video.mp4' }),
});
const { segments } = await transcriptResponse.json();

// Step 3: Render with subtitles
const renderResponse = await fetch('/api/render-final', {
  method: 'POST',
  body: JSON.stringify({
    videoUrl: `http://localhost:8000${output_url}`,
    subtitles: segments,
    template: 'viral',
  }),
});
const { outputUrl } = await renderResponse.json();
```

## Configuration

### Remotion Settings

Edit `remotion/config.ts`:
```typescript
export const REMOTION_CONFIG = {
  DEFAULT_FPS: 30,           // Frames per second
  DEFAULT_WIDTH: 1080,       // Video width
  DEFAULT_HEIGHT: 1920,      // Video height (9:16)
  VIDEO_CODEC: 'h264',       // Output codec
  VIDEO_BITRATE: '4M',       // Quality
  AUDIO_BITRATE: '192k',     // Audio quality
};
```

### Template Customization

Create new template:
```typescript
// remotion/templates/CustomTemplate.tsx
export function CustomTemplate({ currentWord, currentSegment }: CaptionTemplateProps) {
  return (
    <AbsoluteFill>
      {/* Your custom styling */}
      <p style={{ fontSize: '60px' }}>{currentSegment.text}</p>
    </AbsoluteFill>
  );
}
```

Register in `CaptionOverlay.tsx`:
```typescript
{template === 'custom' && <CustomTemplate {...templateProps} />}
```

## Performance Optimization

### Preview Optimization
- Player uses lazy loading
- Templates render only when active
- Smooth animations use `spring()` API

### Rendering Optimization
- Parallel frame rendering enabled
- Hardware acceleration when available
- Configurable quality settings

### Best Practices
1. Keep subtitle segments reasonable length
2. Use word-level timing for precision
3. Test templates before rendering
4. Monitor render progress for long videos

## Troubleshooting

### "Module not found: remotion"
```bash
cd apps/web
pnpm install
```

### Player not displaying
- Check video URL is accessible
- Verify CORS settings on video server
- Ensure subtitles array has valid data

### Render fails
- Check FFmpeg is installed
- Verify output directory exists and is writable
- Check available disk space
- Review server logs for details

### Subtitles out of sync
- Validate subtitle timing with `validateSubtitleTiming()`
- Check frame rate matches source video
- Ensure start/end times are in seconds

## Testing

### Component Testing
```typescript
import { render } from '@testing-library/react';
import { DefaultTemplate } from '@/remotion/templates/DefaultTemplate';

test('renders caption text', () => {
  const { getByText } = render(
    <DefaultTemplate
      currentWord="Hello"
      currentSegment={{ id: 0, start: 0, end: 1, text: "Hello" }}
      isActive={true}
    />
  );
  expect(getByText('Hello')).toBeInTheDocument();
});
```

### Integration Testing
```bash
# Start services
cd apps/processing-engine && python main.py
cd apps/web && pnpm dev

# Test the flow
curl -X POST http://localhost:3000/api/render-final \
  -H "Content-Type: application/json" \
  -d '{"videoUrl":"...","subtitles":[...],"template":"default"}'
```

## Dependencies

```json
{
  "remotion": "^4.0.405",
  "@remotion/player": "^4.0.405",
  "@remotion/renderer": "^4.0.405",
  "@remotion/lambda": "^4.0.405"
}
```

## Next Steps

1. **Database Integration**: Store video projects and render history
2. **Queue System**: Handle multiple renders concurrently
3. **Progress Websockets**: Real-time render progress updates
4. **Custom Fonts**: Add font upload functionality
5. **Advanced Animations**: More template options
6. **Batch Export**: Export multiple clips at once
7. **Cloud Rendering**: Use Remotion Lambda for scale

---

**Status:** ✅ All Phases Complete (P, Q, R, S, T)
**Version:** 1.0.0
**Last Updated:** 2026-01-12
