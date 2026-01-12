# Integration Guide: Python Engine ↔ Content Intelligence

This guide shows how to connect the Python transcription service with the Next.js AI analysis module.

## Architecture Flow

```
Video Upload → Python Processing Engine → Transcript → Next.js AI Module → Viral Clips
```

## Step 1: Get Transcript from Python Engine

The Python service provides transcription via its API:

```typescript
// apps/web/lib/services/transcription.ts
export async function getTranscript(videoFile: File) {
  const formData = new FormData();
  formData.append('video', videoFile);

  const response = await fetch('http://localhost:8000/api/transcribe', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Transcription failed');
  }

  const data = await response.json();
  return data.transcript; // Raw transcript text
}
```

## Step 2: Format Transcript for AI Analysis

Convert the Python engine's output to the format expected by the AI module:

```typescript
// The Python engine returns structured segments
interface PythonTranscriptSegment {
  start: number;
  end: number;
  text: string;
}

// Convert to formatted string for AI analysis
function formatTranscriptForAI(segments: PythonTranscriptSegment[]): string {
  return segments
    .map(segment => {
      const start = formatTime(segment.start);
      const end = formatTime(segment.end);
      return `[${start} - ${end}] ${segment.text}`;
    })
    .join('\n\n');
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}
```

## Step 3: Complete Workflow Component

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useContentAnalysis } from '@/lib/hooks/useContentAnalysis';
import { ViralClipsList } from '@/components/viral-clips-list';

export function VideoAnalysisWorkflow() {
  const [file, setFile] = useState<File | null>(null);
  const [transcript, setTranscript] = useState<string>('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  
  const { analyzeContent, isAnalyzing, analysis } = useContentAnalysis();

  // Step 1: Transcribe with Python engine
  const handleTranscribe = async () => {
    if (!file) return;
    
    setIsTranscribing(true);
    try {
      const formData = new FormData();
      formData.append('video', file);

      const response = await fetch('http://localhost:8000/api/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Transcription failed');
      
      const data = await response.json();
      
      // Format segments into readable transcript
      const formattedTranscript = data.segments
        .map((seg: any) => {
          const start = formatTime(seg.start);
          const end = formatTime(seg.end);
          return `[${start} - ${end}] ${seg.text}`;
        })
        .join('\n\n');
      
      setTranscript(formattedTranscript);
    } catch (error) {
      console.error('Transcription error:', error);
      alert('Failed to transcribe video');
    } finally {
      setIsTranscribing(false);
    }
  };

  // Step 2: Analyze with AI
  const handleAnalyze = async () => {
    if (!transcript) return;
    await analyzeContent(transcript);
  };

  return (
    <div className="space-y-6">
      {/* File Upload */}
      <div>
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <Button
          onClick={handleTranscribe}
          disabled={!file || isTranscribing}
        >
          {isTranscribing ? 'Transcribing...' : 'Step 1: Transcribe Video'}
        </Button>
      </div>

      {/* Transcript Display */}
      {transcript && (
        <div>
          <h3>Transcript Ready</h3>
          <textarea value={transcript} readOnly rows={10} />
          <Button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? 'Analyzing...' : 'Step 2: Find Viral Clips'}
          </Button>
        </div>
      )}

      {/* Results */}
      {analysis && (
        <div>
          <h2>Viral Clips Identified</h2>
          <ViralClipsList clips={analysis.clips} />
        </div>
      )}
    </div>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}
```

## Step 4: Environment Configuration

### Python Engine (.env)
```env
# apps/processing-engine/.env
PORT=8000
HOST=0.0.0.0
```

### Next.js App (.env.local)
```env
# apps/web/.env.local
OPENAI_API_KEY=sk-...
PYTHON_ENGINE_URL=http://localhost:8000
```

## Step 5: CORS Configuration (Python)

Ensure the Python FastAPI service allows requests from Next.js:

```python
# apps/processing-engine/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Running Both Services

### Terminal 1: Python Engine
```bash
cd apps/processing-engine
docker-compose -f docker-compose.dev.yml up
# or
python main.py
```

### Terminal 2: Next.js App
```bash
cd apps/web
pnpm dev
```

## API Data Flow Example

### Request to Python Engine
```bash
POST http://localhost:8000/api/transcribe
Content-Type: multipart/form-data

video: <file>
```

### Response from Python Engine
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 15.3,
      "text": "Hey everyone, welcome back to my channel!"
    },
    {
      "start": 15.3,
      "end": 42.8,
      "text": "Today I'm going to show you something amazing..."
    }
  ],
  "duration": 180.5,
  "language": "en"
}
```

### Request to Next.js AI Module
```bash
POST http://localhost:3000/api/analyze-content
Content-Type: application/json

{
  "transcript": "[00:00 - 00:15] Hey everyone, welcome back...\n\n[00:15 - 00:42] Today I'm going to show you..."
}
```

### Response from AI Module
```json
{
  "success": true,
  "data": {
    "clips": [
      {
        "start_time": 0,
        "end_time": 45,
        "viral_score": 85,
        "summary": "Strong opening hook with clear value proposition",
        "hook": "Promises to show something amazing",
        "conclusion": "Sets up expectation for tutorial"
      }
    ],
    "total_clips": 3,
    "analysis_summary": "Found 3 high-potential clips..."
  }
}
```

## Error Handling

```typescript
async function fullWorkflow(videoFile: File) {
  try {
    // Step 1: Transcribe
    const transcriptResponse = await fetch('http://localhost:8000/api/transcribe', {
      method: 'POST',
      body: formData,
    });
    
    if (!transcriptResponse.ok) {
      throw new Error('Transcription service error');
    }
    
    const { segments } = await transcriptResponse.json();
    const formattedTranscript = formatSegments(segments);
    
    // Step 2: Analyze
    const analysisResponse = await fetch('/api/analyze-content', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript: formattedTranscript }),
    });
    
    if (!analysisResponse.ok) {
      throw new Error('AI analysis error');
    }
    
    const { data } = await analysisResponse.json();
    return data.clips;
    
  } catch (error) {
    console.error('Workflow error:', error);
    throw error;
  }
}
```

## Testing the Integration

### 1. Test Python Engine
```bash
curl -X POST http://localhost:8000/api/transcribe \
  -F "video=@test-video.mp4"
```

### 2. Test Next.js AI Module
```bash
curl -X POST http://localhost:3000/api/analyze-content \
  -H "Content-Type: application/json" \
  -d '{"transcript": "[00:00 - 00:15] Test transcript..."}'
```

### 3. Test Full Integration
```typescript
// Use the VideoAnalysisWorkflow component
// Upload a video, transcribe it, then analyze it
```

## Performance Considerations

1. **Caching**: Cache transcripts to avoid re-processing the same video
2. **Async Processing**: Consider job queues for long videos
3. **Rate Limiting**: Implement rate limits for both services
4. **Streaming**: For large transcripts, consider streaming responses

## Next Steps

- Add database to store transcripts and analyses
- Implement background job processing
- Add webhook support for async workflows
- Create unified error tracking across services
- Add request/response validation middleware
