# Unified Video Processing Workflow

## Overview

This document describes the complete end-to-end video processing workflow in Video Wizard, from upload to final clip creation with subtitle overlay.

## Architecture

The video-container component acts as the **central orchestrator** for all video processing logic, integrating three main systems:

1. **Python Processing Engine** (apps/processing-engine)
   - Video upload and storage
   - Audio extraction and transcription (Whisper)
   - Smart video cropping with face tracking (MediaPipe)
   - Clip rendering (FFmpeg)

2. **AI Content Analysis** (Next.js server)
   - Analyzes transcripts to find viral moments
   - Returns time ranges (start_time, end_time) for each clip
   - Provides viral scores and summaries

3. **Remotion Composition** (Next.js client)
   - Video preview with subtitle overlay
   - 4 caption templates (Default, Viral, Minimal, Modern)
   - Export functionality

## Complete Workflow

### Phase 1: Upload & Transcribe

```
User uploads video
     ↓
useVideoProcessing hook
     ↓
POST /upload (Python) → Saves video file
     ↓
POST /transcribe (Python) → Extracts audio + generates subtitles
     ↓
Returns full transcript with segments
```

**Code Location**: `features/video/hooks/use-video-processing.ts`

**API Endpoints**:
- Python: `POST http://localhost:8000/upload`
- Python: `POST http://localhost:8000/transcribe`

### Phase 2: Content Analysis

```
Full transcript
     ↓
formatTranscriptForAI()
     ↓
POST /api/analyze-content
     ↓
contentAnalysisService.analyzeTranscript()
     ↓
AI generates clips with time_from, time_to, viral_score
     ↓
Returns ContentAnalysis with ViralClip[]
```

**Code Location**: `server/services/content-analysis-service.ts`

**API Endpoint**: `POST /api/analyze-content`

**Data Structure**:
```typescript
interface ViralClip {
  start_time: number;      // time_from in seconds
  end_time: number;        // time_to in seconds
  viral_score: number;     // 0-100
  summary: string;
  hook: string;
  conclusion: string;
}
```

### Phase 3: Clip Creation

When user clicks on a viral clip:

```
handleClipSelect(clip)
     ↓
POST /api/create-clip
     ↓
clipIntegrationService.createClip()
     ↓
Python: POST /render-clip
     ↓
SmartClipper with face tracking
     ↓
Returns clip URL and path
     ↓
POST /api/transcribe (for clip)
     ↓
Returns subtitles for clip
     ↓
Navigate to /editor/new with params
```

**Code Location**: `features/video/containers/video-container.tsx`

**API Endpoints**:
- Next.js: `POST /api/create-clip` (proxy)
- Python: `POST http://localhost:8000/render-clip`
- Next.js: `POST /api/transcribe` (proxy)

**Python Service Call**:
```python
# In SmartClipper
def render_clip(
    video_path: str,
    start_time: float,
    end_time: float,
    crop_mode: str = "dynamic"  # or "static"
)
```

### Phase 4: Editor with Remotion

```
/editor/new?videoUrl=...&clipPath=...
     ↓
VideoEditorPreview component
     ↓
Remotion Player with VideoComposition
     ↓
User selects caption template
     ↓
Real-time preview with subtitles
     ↓
Export button → render final video
```

**Code Location**: 
- `app/editor/[id]/page.tsx`
- `components/video-editor/VideoEditorPreview.tsx`
- `remotion/compositions/VideoComposition.tsx`

## Key Components

### 1. VideoContainer (Orchestrator)

**Location**: `features/video/containers/video-container.tsx`

**Responsibilities**:
- Manages overall workflow state
- Coordinates upload → transcribe → analyze
- Handles clip selection and creation
- Navigates to editor

**Key Methods**:
```typescript
handleClipSelect(clip: ViralClip)      // Create single clip
handleCreateAllClips()                  // Batch create all clips
```

### 2. useVideoProcessing Hook

**Location**: `features/video/hooks/use-video-processing.ts`

**Returns**:
```typescript
{
  file: File | null;
  currentStep: ProcessingStep;
  uploadedPath: string;              // Important for clip creation
  transcription: TranscriptionResult;
  analysis: ContentAnalysis;         // Contains ViralClip[]
  error: string;
  progress: string;
  setFile: (file: File) => void;
  processVideo: () => Promise<void>;
  resetState: () => void;
}
```

### 3. ClipIntegrationService

**Location**: `server/services/clip-integration-service.ts`

**Methods**:
```typescript
createClip(request: ClipRenderRequest): Promise<ClipRenderResponse>
transcribeVideo(videoPath: string): Promise<TranscriptionResponse>
uploadVideo(file: File): Promise<UploadResponse>
getVideoUrl(path: string): string
```

### 4. ContentAnalysisService

**Location**: `server/services/content-analysis-service.ts`

**Methods**:
```typescript
analyzeTranscript(transcript: string): Promise<ContentAnalysis>
validateTranscript(transcript: string): boolean
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     Video Container                          │
│                  (Central Orchestrator)                      │
└────────────┬─────────────────────────────────┬───────────────┘
             │                                 │
             ↓                                 ↓
┌────────────────────────┐         ┌──────────────────────────┐
│  useVideoProcessing    │         │   Individual Clip        │
│        Hook            │         │      Creation            │
└────────┬───────────────┘         └──────────┬───────────────┘
         │                                     │
         ↓                                     ↓
┌────────────────────────┐         ┌──────────────────────────┐
│  Python Engine API     │         │  ClipIntegrationService  │
│  - /upload             │         │  - createClip()          │
│  - /transcribe         │         │  - transcribeVideo()     │
└────────┬───────────────┘         └──────────┬───────────────┘
         │                                     │
         ↓                                     ↓
┌────────────────────────┐         ┌──────────────────────────┐
│  Content Analysis      │         │  Python /render-clip     │
│  Service (AI)          │         │  - SmartClipper          │
│  - Find viral moments  │         │  - Face tracking         │
└────────────────────────┘         └──────────┬───────────────┘
                                               │
                                               ↓
                                   ┌──────────────────────────┐
                                   │  Editor + Remotion       │
                                   │  - Preview with subs     │
                                   │  - Template selection    │
                                   │  - Final export          │
                                   └──────────────────────────┘
```

## Usage Examples

### Single Clip Creation

```typescript
// User clicks on a viral clip in AnalysisResults
const handleClipSelect = async (clip: ViralClip) => {
  // 1. Create vertical clip with Python
  const clipResponse = await fetch('/api/create-clip', {
    method: 'POST',
    body: JSON.stringify({
      video_path: uploadedPath,       // From useVideoProcessing
      start_time: clip.start_time,    // From AI analysis
      end_time: clip.end_time,        // From AI analysis
      crop_mode: 'dynamic',           // Use face tracking
    }),
  });

  // 2. Get subtitles for the clip
  const transcribeResponse = await fetch('/api/transcribe', {
    method: 'POST',
    body: JSON.stringify({
      video_path: clipResult.data.output_path,
    }),
  });

  // 3. Navigate to editor
  router.push(`/editor/new?videoUrl=${clipUrl}&clipPath=${clipPath}`);
};
```

### Batch Clip Creation

```typescript
const handleCreateAllClips = async () => {
  for (const clip of analysis.clips) {
    // Create each clip sequentially
    const response = await fetch('/api/create-clip', {
      method: 'POST',
      body: JSON.stringify({
        video_path: uploadedPath,
        start_time: clip.start_time,
        end_time: clip.end_time,
        crop_mode: 'dynamic',
      }),
    });
  }
};
```

## Environment Configuration

Required environment variables in `.env.local`:

```bash
# Python Processing Engine
NEXT_PUBLIC_PROCESSING_ENGINE_URL=http://localhost:8000

# AI Provider (for content analysis)
OPENAI_API_KEY=your_key_here
# or
ANTHROPIC_API_KEY=your_key_here
```

## API Endpoints Summary

### Next.js API Routes (Proxy)

| Endpoint | Method | Purpose | Proxies To |
|----------|--------|---------|------------|
| `/api/analyze-content` | POST | Analyze transcript for viral moments | Internal AI service |
| `/api/create-clip` | POST | Create vertical clip | Python `/render-clip` |
| `/api/transcribe` | POST | Get subtitles | Python `/transcribe` |

### Python Processing Engine

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/upload` | POST | Upload video file | `{ path, filename }` |
| `/transcribe` | POST | Extract audio + subtitles | `{ segments[], full_text }` |
| `/render-clip` | POST | Create vertical clip | `{ output_url, duration }` |

## Testing the Workflow

1. **Start Python Backend**:
   ```bash
   cd apps/processing-engine
   python main.py
   ```

2. **Start Next.js Frontend**:
   ```bash
   cd apps/web
   pnpm dev
   ```

3. **Upload a Video**:
   - Navigate to `/video-wizard`
   - Upload a video file
   - Wait for processing (upload → transcribe → analyze)

4. **View Results**:
   - See transcription with segments
   - See viral clips with scores and time ranges
   - Click "Create All Clips" or select individual clips

5. **Edit Clip**:
   - Automatically navigates to `/editor/new`
   - Preview with subtitles
   - Select caption template
   - Export final video

## Error Handling

All services implement proper error handling:

```typescript
try {
  const result = await clipIntegrationService.createClip(params);
  if (!result.success) {
    throw new Error(result.error);
  }
} catch (error) {
  logger.error('Clip creation failed', error);
  alert(error instanceof Error ? error.message : 'Unknown error');
}
```

## Type Safety

All data structures are strictly typed:

- ✅ `ViralClip` - Zod schema with TypeScript inference
- ✅ `ContentAnalysis` - Zod schema with validation
- ✅ `ClipRenderRequest` - Zod schema for API
- ✅ `TranscriptionResponse` - Typed response structure
- ✅ `SubtitleSegment` - For Remotion compositions

No `any` types used in the workflow.

## Performance Considerations

- **Sequential Clip Creation**: Clips are created one at a time to avoid overloading the Python backend
- **Progress Indicators**: Real-time feedback for long operations
- **Lazy Loading**: Remotion compositions are loaded on demand
- **Caching**: Uploaded videos and transcriptions are cached

## Future Enhancements

- [ ] WebSocket for real-time progress updates
- [ ] Queue system for concurrent clip rendering
- [ ] Database persistence for projects and clips
- [ ] Cloud rendering with Remotion Lambda
- [ ] Clip preview before creating
- [ ] Batch export all clips at once

---

**Last Updated**: January 2026
**Maintained By**: Video Wizard Team
