# Content Intelligence Module

AI-powered viral clip detection for short-form video content using GPT-4o and Vercel AI SDK.

## Overview

This module analyzes video transcripts to identify the most engaging segments suitable for YouTube Shorts, TikTok, and Instagram Reels. It uses advanced AI to evaluate content based on viral potential criteria.

## Features

- 🤖 **GPT-4o Integration** - Leverages OpenAI's most advanced model for content analysis
- 📊 **Structured Output** - Uses Zod schemas to ensure type-safe, predictable JSON responses
- 🎯 **Viral Scoring** - Assigns 0-100 scores based on engagement potential
- 🎬 **Smart Segmentation** - Identifies clips with strong hooks and conclusions
- ⏱️ **Optimal Length** - Focuses on 30-90 second segments perfect for short-form platforms
- 🔍 **Detailed Analysis** - Provides reasoning for each clip selection

## Installation

### Prerequisites

- Node.js 18+ and pnpm
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Setup

1. **Install dependencies**:
   ```bash
   cd apps/web
   pnpm install
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-...
   ```

3. **Run the development server**:
   ```bash
   pnpm dev
   ```

4. **Access the module**:
   Navigate to `http://localhost:3000/content-intelligence`

## Architecture

### API Route
**Location**: `app/api/analyze-content/route.ts`

The API endpoint accepts POST requests with a transcript and returns structured analysis:

```typescript
// Request
POST /api/analyze-content
{
  "transcript": "Your video transcript here..."
}

// Response
{
  "success": true,
  "data": {
    "clips": [
      {
        "start_time": 0,
        "end_time": 45,
        "viral_score": 85,
        "summary": "Strong opening hook about surprising statistic",
        "hook": "90% of YouTubers quit in first year",
        "conclusion": "Teases the secret solution"
      }
    ],
    "total_clips": 3,
    "analysis_summary": "Found 3 high-potential clips..."
  }
}
```

### The "Viral Editor" Prompt

The system prompt instructs GPT-4o to think like an expert video editor:

**Key Criteria**:
- ✅ Strong hooks (questions, bold statements, surprising facts)
- ✅ Complete thoughts (no mid-sentence cuts)
- ✅ Emotional impact (curiosity, laughter, surprise)
- ✅ Optimal length (30-90 seconds)
- ✅ Clear conclusions
- ✅ Standalone value (understandable without full context)
- ✅ Shareability

**Scoring System**:
- **90-100**: Extremely viral potential
- **70-89**: High potential
- **50-69**: Good potential
- **30-49**: Moderate potential
- **0-29**: Low potential

### Structured Data with Zod

We use Zod schemas to enforce strict type safety:

```typescript
const ViralClipSchema = z.object({
  start_time: z.number(),
  end_time: z.number(),
  viral_score: z.number().min(0).max(100),
  summary: z.string(),
  hook: z.string().optional(),
  conclusion: z.string().optional(),
});
```

This prevents parsing errors and ensures consistent output from the LLM.

## Usage

### Client-Side Hook

Use the `useContentAnalysis` hook in your React components:

```typescript
import { useContentAnalysis } from '@/lib/hooks/useContentAnalysis';

function MyComponent() {
  const { analyzeContent, isAnalyzing, analysis, error } = useContentAnalysis({
    onSuccess: (data) => {
      console.log('Found clips:', data.clips);
    },
  });

  const handleAnalyze = async () => {
    const result = await analyzeContent(transcript);
    // Do something with result
  };

  return (
    <button onClick={handleAnalyze} disabled={isAnalyzing}>
      {isAnalyzing ? 'Analyzing...' : 'Analyze'}
    </button>
  );
}
```

### Direct API Usage

```typescript
const response = await fetch('/api/analyze-content', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ transcript: 'Your transcript...' }),
});

const data = await response.json();
console.log(data.data.clips);
```

## Components

### ViralClipCard

Displays individual clip information with visual scoring:

```typescript
import { ViralClipCard } from '@/components/viral-clips-list';

<ViralClipCard 
  clip={clip} 
  index={0}
  onSelect={(clip) => console.log(clip)}
/>
```

### ViralClipsList

Shows all identified clips sorted by viral score:

```typescript
import { ViralClipsList } from '@/components/viral-clips-list';

<ViralClipsList 
  clips={analysis.clips}
  onClipSelect={(clip) => {
    // Handle clip selection (e.g., jump to timestamp)
  }}
/>
```

## Integration with Processing Engine

This module is designed to work with the Python transcription service:

```typescript
// 1. Get transcript from Python engine
const transcriptResponse = await fetch('http://localhost:8000/api/transcribe', {
  method: 'POST',
  body: formData,
});
const { transcript } = await transcriptResponse.json();

// 2. Analyze with AI
const analysisResponse = await fetch('/api/analyze-content', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ transcript }),
});
const { data } = await analysisResponse.json();

// 3. Use the identified clips
data.clips.forEach(clip => {
  console.log(`Clip ${clip.start_time}s - ${clip.end_time}s: ${clip.viral_score}`);
});
```

## Best Practices

1. **Transcript Format**: Include timestamps for better accuracy:
   ```
   [00:00 - 00:15] Opening hook text here...
   [00:15 - 00:45] Main content...
   ```

2. **Error Handling**: Always handle API errors gracefully:
   ```typescript
   const { error } = useContentAnalysis({
     onError: (err) => {
       toast.error(`Analysis failed: ${err}`);
     },
   });
   ```

3. **Rate Limiting**: OpenAI has rate limits. Consider implementing:
   - Request queuing
   - Retry logic with exponential backoff
   - Caching results for identical transcripts

4. **Cost Optimization**: 
   - Cache results in database
   - Only analyze when content changes
   - Consider using GPT-4o-mini for lower costs during development

## Testing

Test the API with curl:

```bash
curl -X POST http://localhost:3000/api/analyze-content \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "[00:00-00:30] This is a test transcript with an engaging hook!"
  }'
```

## Troubleshooting

### "OpenAI API key not configured"
- Ensure `.env.local` exists with `OPENAI_API_KEY`
- Restart the development server after adding env vars

### Poor clip quality
- Provide more detailed transcripts
- Include timestamps for better context
- Ensure transcript is clear and well-formatted

### Rate limit errors
- Check your OpenAI usage limits
- Implement request throttling
- Consider upgrading your OpenAI plan

## Future Enhancements

- [ ] Multi-language support
- [ ] Customizable viral criteria
- [ ] A/B testing for different prompts
- [ ] Thumbnail suggestion based on clip content
- [ ] Automatic title generation for clips
- [ ] Integration with video editing APIs
- [ ] Batch processing for multiple videos
- [ ] Analytics dashboard for clip performance

## API Reference

### Types

```typescript
interface ViralClip {
  start_time: number;      // Start time in seconds
  end_time: number;        // End time in seconds
  viral_score: number;     // Score from 0-100
  summary: string;         // Why this clip is engaging
  hook?: string;           // The attention-grabbing element
  conclusion?: string;     // How the clip ends
}

interface ContentAnalysis {
  clips: ViralClip[];
  total_clips: number;
  analysis_summary: string;
}
```

### Endpoints

#### POST /api/analyze-content

Analyzes a transcript and returns viral clip suggestions.

**Request Body**:
```typescript
{
  transcript: string;  // Required: The video transcript to analyze
}
```

**Response**:
```typescript
{
  success: boolean;
  data?: ContentAnalysis;
  error?: string;
  details?: string;
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad request (missing transcript)
- `500`: Server error (API key missing, OpenAI error)

## License

Part of the Video Wizard monorepo project.
