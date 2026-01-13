# Video Export Strategy

## Current Setup (✅ Working)

### Preview with Remotion Player
- **Client-side only** using `@remotion/player`
- Real-time preview with subtitle synchronization
- Template switching (Default, Viral, Minimal, Modern)
- No server-side rendering needed
- **Location**: `components/video-editor/VideoEditorPreview.tsx`

### Why No Server-Side Rendering?

Calling `@remotion/bundler` and `@remotion/renderer` in Next.js API routes causes bundling issues:
- Webpack tries to bundle the bundler itself
- Missing native compositor binaries
- Complex webpack configuration needed

**Reference**: https://www.remotion.dev/docs/troubleshooting/bundling-bundle

## Export Options

### Option 1: Python FFmpeg Backend (Recommended for MVP)

Use the existing Python backend to burn in subtitles with FFmpeg.

**Implementation**:
```python
# In processing-engine/renderer.py
def add_subtitles_to_video(
    video_path: str,
    subtitles: List[Subtitle],
    style: str = "default"
) -> str:
    """
    Burn subtitles into video using FFmpeg
    """
    # Generate SRT file
    srt_path = create_srt_file(subtitles)
    
    # Apply style based on template
    subtitle_style = get_subtitle_style(style)
    
    # FFmpeg command with subtitle filter
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"subtitles={srt_path}:force_style='{subtitle_style}'",
        '-c:a', 'copy',
        output_path
    ]
```

**Pros**:
- Fast and reliable
- No bundling issues
- Works on server
- Full control over styling

**Cons**:
- Less fancy than Remotion templates
- Need to replicate template styles in FFmpeg

### Option 2: Client-Side Recording

Use `@remotion/player` with MediaRecorder API to record the canvas.

**Implementation**:
```typescript
// In components/video-editor/ExportControls.tsx
async function exportVideo() {
  const player = playerRef.current;
  
  // Use MediaRecorder to capture canvas
  const stream = player.getCanvas().captureStream();
  const recorder = new MediaRecorder(stream);
  
  // Record while playing
  player.play();
  recorder.start();
  
  // Stop when done
  player.addEventListener('ended', () => {
    recorder.stop();
  });
}
```

**Pros**:
- Uses existing Remotion templates
- No server-side rendering
- Works in browser

**Cons**:
- Slower than server rendering
- Quality depends on playback performance
- User must keep browser open

### Option 3: Remotion Lambda (Production)

Deploy pre-built Remotion bundle to AWS Lambda.

**Setup**:
```bash
# 1. Create Remotion bundle
npx remotion bundle remotion/index.ts --bundle-cache ./remotion-bundle

# 2. Deploy to Lambda
npx remotion lambda sites create remotion-bundle

# 3. Render on Lambda
npx remotion lambda render [site-id] VideoWithSubtitles output.mp4 --props='{"videoUrl":"...","subtitles":[...]}'
```

**Pros**:
- Fast server-side rendering
- Scales automatically
- Professional solution

**Cons**:
- AWS costs
- Complex setup
- Overkill for MVP

### Option 4: Standalone Node.js Script

Create a separate Node.js script (not bundled by Next.js) that uses `@remotion/bundler`.

**Implementation**:
```typescript
// scripts/render-video.ts (not in Next.js)
import { bundle } from '@remotion/bundler';
import { renderMedia } from '@remotion/renderer';

async function renderVideo(params) {
  // Bundle once at startup
  const bundleLocation = await bundle({
    entryPoint: './remotion/index.ts'
  });
  
  // Render with bundle
  await renderMedia({
    serveUrl: bundleLocation,
    composition,
    outputLocation: 'output.mp4'
  });
}
```

Run separately:
```bash
node scripts/render-video.ts
```

**Pros**:
- Full Remotion capabilities
- No bundling conflicts
- Good for long-running server

**Cons**:
- Separate process management
- Not integrated with Next.js API

## Recommendation

### For Current Implementation (MVP):
**Use Python FFmpeg Backend** (Option 1)

1. Already have Python backend running
2. FFmpeg is battle-tested for video processing
3. Can replicate basic Remotion template styles
4. Fast and reliable

### Implementation Steps:

1. **Add subtitle styling to Python**:
   ```python
   # processing-engine/subtitle_styles.py
   STYLES = {
       'default': 'FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000',
       'viral': 'FontSize=32,PrimaryColour=&H00FFFF,Bold=1',
       'minimal': 'FontSize=20,PrimaryColour=&HFFFFFF',
       'modern': 'FontSize=28,PrimaryColour=&HFF6B6B'
   }
   ```

2. **Add FFmpeg subtitle filter**:
   ```python
   def render_with_subtitles(video_path, subtitles, template):
       srt_file = create_srt(subtitles)
       style = STYLES[template]
       
       subprocess.run([
           'ffmpeg',
           '-i', video_path,
           '-vf', f"subtitles={srt_file}:force_style='{style}'",
           '-c:a', 'copy',
           output_path
       ])
   ```

3. **Update API endpoint**:
   ```python
   @app.post("/export-with-subtitles")
   async def export_with_subtitles(request: ExportRequest):
       output = render_with_subtitles(
           video_path=request.video_path,
           subtitles=request.subtitles,
           template=request.template
       )
       return {"output_url": output}
   ```

4. **Call from Next.js**:
   ```typescript
   // In ExportControls.tsx
   async function exportVideo() {
       const response = await fetch('/api/export-subtitled-video', {
           method: 'POST',
           body: JSON.stringify({
               video_path: clipPath,
               subtitles: subtitles,
               template: selectedTemplate
           })
       });
       
       const { output_url } = await response.json();
       // Download link
   }
   ```

### For Future (Production):
**Remotion Lambda** (Option 3)

When you need:
- High-quality exports
- Complex animations
- Scalability
- Professional features

## Current Status

✅ **Preview**: Working with `@remotion/player`  
❌ **Export**: Removed server-side rendering (causing bundling issues)  
🎯 **Next Step**: Implement Python FFmpeg subtitle export

---

**Documentation**: https://www.remotion.dev/docs/ssr-node  
**FFmpeg Subtitles**: https://ffmpeg.org/ffmpeg-filters.html#subtitles
