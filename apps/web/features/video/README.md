# Video Feature Module

This module implements the complete video processing workflow using a screaming architecture pattern.

## Overview

The video feature handles:
- Video file upload and validation
- Transcription generation via Python engine
- AI-powered content analysis
- Viral clip detection and ranking

## Architecture

This module follows the **screaming architecture** pattern with separation between:

- **Components** (`components/`): Atomic, presentational React components (client-side)
- **Containers** (`containers/`): Client-side components that orchestrate state and logic
- **Hooks** (`hooks/`): Custom React hooks for state management and side effects
- **Types** (`types/`): TypeScript interfaces and type definitions
- **Utils** (`lib/`): Utility functions and helpers

### Component Patterns

We use two component patterns:

#### Presentational Components
- Pure and atomic
- Receive data via props
- Emit events via callbacks
- Don't contain business logic
- Are highly reusable

#### Container Components
- Use 'use client' directive
- Manage state with hooks
- Orchestrate presentational components
- Handle lifecycle events
- Provide data to child components

## Module Structure

```
features/video/
├── components/           # Presentational components
│   ├── video-header.tsx
│   ├── video-uploader.tsx
│   ├── processing-progress.tsx
│   ├── transcription-results.tsx
│   ├── analysis-results.tsx
│   ├── video-how-it-works.tsx
│   └── index.ts         # Component exports
├── containers/          # Container components
│   └── video-container.tsx  # Main workflow orchestrator
├── hooks/               # Custom hooks
│   └── use-video-processing.ts
├── types/               # Type definitions
│   └── index.ts
├── lib/                 # Utilities
│   └── utils.ts
├── index.ts             # Main module export
└── README.md            # This file
```

## Usage

### Recommended: Using Container Component (Server Page)

```tsx
// app/video-wizard/page.tsx (Server Component)
import { VideoContainer } from '@/features/video/containers/video-container';

export default function VideoWizardPage() {
  return <VideoContainer />;
}
```

This is the **recommended approach** because:
- Pages remain server components by default
- Better for performance and SEO
- Follows Next.js App Router best practices
- Cleaner separation of concerns

### Alternative: Direct Hook Usage (Client Component)

If you need custom orchestration logic:

```tsx
'use client';

import {
  VideoHeader,
  VideoUploader,
  ProcessingProgress,
  TranscriptionResults,
  AnalysisResults,
  VideoHowItWorks,
  useVideoProcessing,
} from '@/features/video';

export default function CustomVideoPage() {
  const {
    file,
    currentStep,
    transcription,
    analysis,
    error,
    progress,
    setFile,
    processVideo,
    resetState,
  } = useVideoProcessing({
    onComplete: (data) => console.log('Done!', data),
    onError: (err) => console.error('Error:', err),
  });

  return (
    <div>
      <VideoHeader />
      <VideoUploader
        file={file}
        currentStep={currentStep}
        onFileSelect={setFile}
        onProcess={processVideo}
        onReset={resetState}
        error={error}
      />
      <ProcessingProgress
        currentStep={currentStep}
        progress={progress}
        error={error}
      />
      {transcription && <TranscriptionResults transcription={transcription} />}
      {analysis && <AnalysisResults analysis={analysis} />}
    </div>
  );
}
```

## Containers

### VideoContainer

Main container component that orchestrates the video processing workflow.

**Location**: `containers/video-container.tsx`

**Type**: Client Component ('use client')

**Features**:
- Uses `useVideoProcessing` hook for state management
- Composes all presentational components
- Handles workflow lifecycle
- Provides callbacks for events

**Usage**:
```tsx
import { VideoContainer } from '@/features/video/containers/video-container';

// In your server component page
export default function Page() {
  return <VideoContainer />;
}
```

**Why use containers?**
- Keep pages as server components
- Better performance (smaller client bundle)
- Improved SEO
- Follows Next.js best practices
- Clear separation between server and client code

## Components

### VideoHeader
Displays the feature title, description, and badges.
- **Props**: None
- **Usage**: Static header component

### VideoUploader
Handles file selection and upload initiation.
- **Props**: `file`, `currentStep`, `onFileSelect`, `onProcess`, `onReset`, `error`
- **Validation**: File type (video/*), size (max 500MB)

### ProcessingProgress
Shows step-by-step progress through the workflow.
- **Props**: `currentStep`, `progress`, `error`
- **Steps**: Upload → Transcribe → Analyze

### TranscriptionResults
Displays the generated transcript with timestamps.
- **Props**: `transcription`
- **Format**: `[MM:SS - MM:SS] Text`

### AnalysisResults
Shows AI analysis summary and viral clip recommendations.
- **Props**: `analysis`, `onClipSelect`
- **Features**: Summary, clip list with scores

### VideoHowItWorks
Informational component explaining the workflow.
- **Props**: None
- **Usage**: Shown when idle

## Hooks

### useVideoProcessing

Main hook for video processing workflow.

**Parameters:**
```typescript
{
  onComplete?: (data: { transcription, analysis }) => void;
  onError?: (error: Error) => void;
}
```

**Returns:**
```typescript
{
  file: File | null;
  currentStep: ProcessingStep;
  transcription: TranscriptionResult | null;
  analysis: ContentAnalysis | null;
  error: string;
  progress: string;
  setFile: (file: File | null) => void;
  processVideo: () => Promise<void>;
  resetState: () => void;
}
```

**Workflow:**
1. Upload video to Python engine (`/upload`)
2. Transcribe video (`/transcribe`)
3. Analyze content with AI (`/api/analyze-content`)

## Types

### ProcessingStep
```typescript
type ProcessingStep = 
  | 'idle' 
  | 'uploading' 
  | 'transcribing' 
  | 'analyzing' 
  | 'complete' 
  | 'error';
```

### TranscriptSegment
```typescript
interface TranscriptSegment {
  id: number;
  start: number;
  end: number;
  text: string;
}
```

### TranscriptionResult
```typescript
interface TranscriptionResult {
  video_path: string;
  audio_path?: string;
  segments: TranscriptSegment[];
  full_text: string;
  segment_count: number;
}
```

### VideoProcessingState
```typescript
interface VideoProcessingState {
  file: File | null;
  currentStep: ProcessingStep;
  uploadedPath: string;
  transcription: TranscriptionResult | null;
  analysis: ContentAnalysis | null;
  error: string;
  progress: string;
}
```

## Utilities

### formatTimestamp
Converts seconds to `MM:SS` format.

```typescript
formatTimestamp(125) // "02:05"
```

### formatTranscriptForAI
Formats transcript segments for AI analysis.

```typescript
const formatted = formatTranscriptForAI(segments);
// "[00:00 - 00:05] Hello world\n\n[00:05 - 00:10] Next segment"
```

### validateVideoFile
Validates file type and size.

```typescript
const error = validateVideoFile(file);
// Returns error message or null
```

## Configuration

The module uses environment variables:

```env
NEXT_PUBLIC_PYTHON_ENGINE_URL=http://localhost:8000
```

## Integration

This feature integrates with:
- **Python Processing Engine**: Video upload and transcription
- **Content Analysis Service**: AI-powered clip detection
- **Server Services**: `@/server/services/content-analysis-service`

## Testing

```typescript
// Example test
import { validateVideoFile } from '@/features/video/lib/utils';

test('validates video file', () => {
  const file = new File(['content'], 'video.mp4', { type: 'video/mp4' });
  expect(validateVideoFile(file)).toBeNull();
});
```

## Future Enhancements

- [ ] Add video player for clip preview
- [ ] Support batch video processing
- [ ] Add progress percentage tracking
- [ ] Implement clip editing interface
- [ ] Add export functionality
- [ ] Support multiple languages

## Related Documentation

- [Project Instructions](../../.copilot/project-instructions.md)
- [Code Patterns](../../.copilot/code-patterns.md)
- [Server Module](../../server/README.md)
- [Content Analysis Service](../../server/services/content-analysis-service.ts)
