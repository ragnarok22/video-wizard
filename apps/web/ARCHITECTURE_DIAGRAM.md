# Video Wizard - Complete Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          VIDEO-CONTAINER.TSX                                │
│                    (Central Integration Point)                              │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  useVideoProcessing() Hook                                           │  │
│  │  ────────────────────────                                            │  │
│  │  • file: File                                                        │  │
│  │  • uploadedPath: string  ◄──── IMPORTANT: Used for clip creation    │  │
│  │  • transcription: TranscriptionResult                                │  │
│  │  • analysis: ContentAnalysis  ◄──── Contains viral clips            │  │
│  │  • processVideo()                                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  handleClipSelect(clip: ViralClip)                                   │  │
│  │  ──────────────────────────────────                                  │  │
│  │  1. Extract time_from (start_time) and time_to (end_time)           │  │
│  │  2. Call /api/create-clip with uploadedPath + time range            │  │
│  │  3. Call /api/transcribe for clip subtitles                         │  │
│  │  4. Navigate to /editor with clip URL + subtitles                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ↓                           ↓                           ↓
┌───────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│ PYTHON BACKEND    │    │  AI ANALYSIS         │    │  REMOTION ENGINE     │
│ (Port 8000)       │    │  (Next.js Server)    │    │  (Client Side)       │
└───────────────────┘    └──────────────────────┘    └──────────────────────┘
        │                           │                           │
        │                           │                           │
┌───────┴────────┐         ┌────────┴─────────┐      ┌─────────┴──────────┐
│  /upload       │         │  /api/analyze-   │      │  VideoComposition  │
│  ──────        │         │   content        │      │  ───────────────   │
│  • Stores video│         │  ──────────────  │      │  • VideoPlayer     │
│  • Returns path│         │  • Sends         │      │  • CaptionOverlay  │
│                │         │    transcript    │      │                    │
│  /transcribe   │         │  • Gets viral    │      │  Templates:        │
│  ──────────    │         │    moments       │      │  • Default         │
│  • Whisper AI  │         │  • Returns       │      │  • Viral           │
│  • Audio →     │         │    time ranges   │      │  • Minimal         │
│    Segments    │         │                  │      │  • Modern          │
│                │         │  Returns:        │      │                    │
│  /render-clip  │         │  {               │      │  Input:            │
│  ────────────  │         │    clips: [{     │      │  • videoUrl        │
│  • SmartClipper│         │      start_time, │      │  • subtitles[]     │
│  • Face track  │         │      end_time,   │      │  • template        │
│  • FFmpeg crop │         │      score       │      │                    │
│  • Returns URL │         │    }]            │      │  Output:           │
│                │         │  }               │      │  • Preview player  │
│                │         │                  │      │  • Export video    │
└────────────────┘         └──────────────────┘      └────────────────────┘
```

## Data Flow Example

### Upload & Analysis Phase

```
User uploads "podcast.mp4"
         ↓
POST /upload → "uploads/podcast_abc123.mp4"
         ↓
uploadedPath = "uploads/podcast_abc123.mp4" [STORED IN STATE]
         ↓
POST /transcribe → { segments: [...], full_text: "..." }
         ↓
POST /api/analyze-content → {
  clips: [
    {
      start_time: 45.2,    ← time_from
      end_time: 67.8,      ← time_to
      viral_score: 92,
      summary: "Shocking revelation about AI"
    },
    {
      start_time: 120.5,
      end_time: 145.0,
      viral_score: 85,
      summary: "Funny joke that went viral"
    }
  ]
}
```

### Clip Creation Phase

```
User clicks on clip #1 (score: 92)
         ↓
handleClipSelect({
  start_time: 45.2,
  end_time: 67.8,
  ...
})
         ↓
POST /api/create-clip
{
  video_path: "uploads/podcast_abc123.mp4",  ← uploadedPath
  start_time: 45.2,                          ← from viral clip
  end_time: 67.8,                            ← from viral clip
  crop_mode: "dynamic"                       ← face tracking
}
         ↓
Python SmartClipper:
• Loads video
• Detects faces from 45.2s to 67.8s
• Crops to 9:16 vertical format
• Tracks main face
• Renders with FFmpeg
         ↓
Returns: {
  output_url: "http://localhost:8000/output/clip_xyz789.mp4",
  output_path: "uploads/clip_xyz789.mp4",
  duration: 22.6
}
         ↓
POST /api/transcribe
{
  video_path: "uploads/clip_xyz789.mp4"
}
         ↓
Returns: {
  segments: [
    { start: 0, end: 3.5, text: "So here's the thing..." },
    { start: 3.5, end: 7.2, text: "AI is going to change everything" },
    ...
  ]
}
         ↓
router.push(`/editor/new?videoUrl=...&clipPath=...`)
         ↓
Editor Page:
• Remotion Player loads clip
• Subtitles sync to frames
• User selects "Viral" template
• Exports with burned-in captions
```

## Key Integration Points

### 1. uploadedPath Bridge

```typescript
// Stored from upload
const uploadedPath = "uploads/podcast_abc123.mp4";

// Used in clip creation
{
  video_path: uploadedPath,      // Source video
  start_time: clip.start_time,   // From AI
  end_time: clip.end_time,       // From AI
}
```

### 2. Time Range Bridge

```typescript
// AI provides
const clip = {
  start_time: 45.2,  // time_from
  end_time: 67.8,    // time_to
};

// Python uses
render_clip(
  video_path="uploads/podcast_abc123.mp4",
  start_time=45.2,   // Extract from here
  end_time=67.8      // To here
)
```

### 3. Subtitle Bridge

```typescript
// Python provides segments
const segments = [
  { start: 0, end: 3.5, text: "..." },
  { start: 3.5, end: 7.2, text: "..." },
];

// Remotion renders
<CaptionOverlay
  subtitles={segments}
  template="viral"
  currentFrame={frame}
/>
```

## Files Changed

### Core Integration
- ✅ `features/video/containers/video-container.tsx` - Main orchestrator
- ✅ `features/video/types/index.ts` - Fixed `any` → `ContentAnalysis`
- ✅ `features/video/components/analysis-results.tsx` - Proper types
- ✅ `components/viral-clips-list.tsx` - Import path fix

### Services (Already Existed)
- ✅ `server/services/clip-integration-service.ts`
- ✅ `server/services/content-analysis-service.ts`
- ✅ `app/api/create-clip/route.ts`
- ✅ `app/api/transcribe/route.ts`
- ✅ `app/api/analyze-content/route.ts`

### Documentation
- ✅ `docs/UNIFIED_VIDEO_WORKFLOW.md` - Complete workflow guide
- ✅ `features/video/containers/INTEGRATION_SUMMARY.md` - Quick reference
- ✅ `ARCHITECTURE_DIAGRAM.md` - This file

## Testing Checklist

- [ ] Upload video → verify uploadedPath stored
- [ ] Transcribe → verify segments returned
- [ ] Analyze → verify viral clips with time ranges
- [ ] Click single clip → verify navigation to editor
- [ ] Click "Create All Clips" → verify batch processing
- [ ] Editor preview → verify subtitles sync
- [ ] Export → verify final video with captions

## Status: ✅ FULLY INTEGRATED

All isolated features are now connected through the video-container component.
