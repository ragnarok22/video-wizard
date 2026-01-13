# Smart Video Clipper - Implementation Documentation

## Overview
The Smart Video Clipper service creates vertical short clips (9:16 aspect ratio) from horizontal videos with intelligent face tracking and smooth camera movement.

## Architecture

### Components

1. **SmartClipper Class** (`smart_clipper.py`)
   - Main service class that orchestrates the entire clipping pipeline
   - Implements face detection, coordinate smoothing, and video rendering
   - Uses MediaPipe for face detection and FFmpeg for video processing

2. **API Endpoint** (`/render-clip` in `main.py`)
   - RESTful endpoint for creating clips via HTTP requests
   - Validates inputs and handles errors gracefully
   - Returns comprehensive metadata about the generated clip

## Implementation Details

### Phase L: Face Tracking Algorithm
**Location:** `SmartClipper._track_faces_in_range()`

**Purpose:** Calculate optimal crop position for each frame to keep the speaker centered.

**Process:**
1. Opens video file and extracts metadata (fps, resolution)
2. Calculates 9:16 crop dimensions based on video height
3. Jumps to the start frame of the requested time range
4. For each frame in the range:
   - Detects faces using MediaPipe Face Detection
   - Calculates the X-coordinate where the crop window should be positioned
   - Centers the crop on the detected face
   - Constrains position to video boundaries
   - Falls back to center crop if no face detected
5. Returns list of X-coordinates (one per frame)

**Key Features:**
- Full-range face detection model for better accuracy
- Boundary checking to prevent cropping outside video
- Graceful fallback when no faces are detected

### Phase M: Path Smoothing
**Location:** `SmartClipper._smooth_coordinates()`

**Purpose:** Apply cinematic stabilization to prevent jittery camera movement.

**Process:**
1. Receives raw X-coordinates from face tracking
2. Applies a **Moving Average Filter** using NumPy convolution
3. Window size (default: 30 frames) controls smoothing strength
4. Returns smoothed coordinates that simulate steady camera panning

**Technical Details:**
```python
smoothed = np.convolve(
    coords_array,
    np.ones(smoothing_window) / smoothing_window,
    mode='same'
)
```

**Effect:**
- Eliminates frame-to-frame jitter
- Creates professional-looking camera movement
- Maintains general tracking direction while removing noise

### Phase N: FFmpeg Rendering
**Location:** `SmartClipper._render_clip()`

**Purpose:** Create the physical video file with trimming and cropping applied.

**Modes:**

#### Static Crop Mode
- Calculates average position from smoothed coordinates
- Applies fixed crop at that position
- Faster rendering, good for videos with minimal movement
- Command: `ffmpeg -ss START -t DURATION -i INPUT -vf crop=W:H:X:Y OUTPUT`

#### Dynamic Crop Mode (In Progress)
- Would use smoothed coordinates to pan the crop window over time
- Currently falls back to static crop with average position
- Future enhancement: Use FFmpeg zoompan or sendcmd filters

**FFmpeg Parameters:**
- `-ss`: Start time (seeking)
- `-t`: Duration (length of clip)
- `-vf crop=W:H:X:Y`: Video filter for cropping
- `-c:a copy`: Copy audio stream without re-encoding
- `-preset fast`: Balance between speed and file size

### Phase O: API Endpoint
**Location:** `POST /render-clip` in `main.py`

**Request Schema:**
```json
{
  "video_path": "/uploads/my_video.mp4",
  "start_time": 10.5,
  "end_time": 40.0,
  "crop_mode": "dynamic",
  "output_path": "/output/custom_name.mp4"  // optional
}
```

**Response Schema:**
```json
{
  "success": true,
  "output_path": "/output/clip_10s.mp4",
  "crop_mode": "static",
  "duration": 29.5,
  "crop_dimensions": {
    "width": 608,
    "height": 1080
  },
  "file_size": 5242880,
  "start_time": 10.5,
  "end_time": 40.0
}
```

**Validations:**
- Video file must exist
- start_time must be >= 0
- start_time must be < end_time
- crop_mode must be "dynamic" or "static"

**Error Handling:**
- 404: Video file not found
- 400: Invalid input parameters
- 500: Processing errors (FFmpeg, face detection, etc.)

## Usage Examples

### Via API

```bash
# Create a 30-second clip with face tracking
curl -X POST http://localhost:8000/render-clip \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/uploads/lecture.mp4",
    "start_time": 120.0,
    "end_time": 150.0,
    "crop_mode": "dynamic"
  }'
```

### Direct Python Usage

```python
from smart_clipper import SmartClipper

clipper = SmartClipper(smoothing_window=30)

result = clipper.create_clip(
    video_path="input.mp4",
    start_time=60.0,
    end_time=90.0,
    output_path="output/short.mp4",
    crop_mode="static"
)

print(f"Clip created: {result['output_path']}")
print(f"Duration: {result['duration']}s")
```

## Configuration

### Smoothing Window
Controls how much smoothing is applied to camera movement:
- **Small (10-20 frames):** More responsive, follows face closely
- **Medium (30-40 frames):** Balanced, default setting
- **Large (50+ frames):** Very smooth, may lag behind fast movements

```python
clipper = SmartClipper(smoothing_window=40)
```

### Face Detection Confidence
Adjust in the `SmartClipper.__init__()` method:
```python
self.face_detection = self.mp_face_detection.FaceDetection(
    model_selection=1,  # 0=short-range, 1=full-range
    min_detection_confidence=0.5  # 0.0 to 1.0
)
```

## Performance Considerations

### Processing Time
- Face detection: ~30-60ms per frame (depends on resolution)
- For a 30-second clip at 30fps: ~900 frames = ~30-60 seconds processing
- FFmpeg rendering: Additional 10-30 seconds depending on video size

### Optimizations
1. **Frame Sampling:** Process every Nth frame for faster analysis
2. **Resolution:** Downscale frames for face detection (maintaining accuracy)
3. **GPU Acceleration:** Use CUDA/Metal for MediaPipe (if available)
4. **FFmpeg Hardware Encoding:** Use `-c:v h264_videotoolbox` on macOS

## Dependencies

```txt
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
ffmpeg-python>=0.2.0
```

**System Requirements:**
- FFmpeg installed (`brew install ffmpeg` on macOS)
- Python 3.11+
- Sufficient RAM for video processing (4GB+ recommended)

## Limitations & Future Enhancements

### Current Limitations
1. Dynamic cropping falls back to static (not fully implemented)
2. Only detects one face (the first detected)
3. No audio-based speaker detection
4. No custom aspect ratios (fixed at 9:16)

### Planned Enhancements
1. **True Dynamic Cropping:** Implement FFmpeg zoompan filter with frame-by-frame coordinates
2. **Multi-Face Support:** Detect multiple speakers and choose the active one
3. **Audio Analysis:** Use speech detection to identify the active speaker
4. **Custom Aspect Ratios:** Support 1:1, 4:5, etc. for different platforms
5. **Batch Processing:** Create multiple clips from a single video in one pass
6. **Preview Generation:** Quick low-res preview before full render
7. **Background Blur:** Add blur/solid color to sides if source is narrower than 9:16

## Troubleshooting

### "FFmpeg not found"
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
apt-get install ffmpeg

# Check installation
ffmpeg -version
```

### "No faces detected"
- Ensure video has sufficient lighting
- Check if faces are visible in the frame
- Try lowering `min_detection_confidence`
- Service automatically falls back to center crop

### Slow Processing
- Reduce `smoothing_window` parameter
- Use `crop_mode="static"` for faster rendering
- Ensure video file is on local disk (not network drive)
- Consider downscaling large 4K videos first

## Testing

### Manual Test
```bash
# Start the service
cd apps/processing-engine
python main.py

# Test the endpoint
curl -X POST http://localhost:8000/render-clip \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "uploads/test.mp4",
    "start_time": 0,
    "end_time": 10,
    "crop_mode": "static"
  }'
```

### Unit Tests (To be created)
```python
# tests/test_smart_clipper.py
import pytest
from smart_clipper import SmartClipper

def test_create_clip():
    clipper = SmartClipper()
    result = clipper.create_clip(
        video_path="test_video.mp4",
        start_time=0,
        end_time=5,
        output_path="output/test_clip.mp4",
        crop_mode="static"
    )
    assert result["success"] == True
    assert os.path.exists(result["output_path"])
```

## Integration with Video Wizard

The Smart Clipper integrates with the larger Video Wizard application:

1. **Upload Video:** User uploads video via `/upload` endpoint
2. **Transcribe:** Get transcript with timestamps via `/transcribe`
3. **Analyze Content:** Identify viral moments via content analysis
4. **Create Clips:** Use `/render-clip` to generate shorts from viral segments
5. **Download:** User downloads the generated clips

### Example Workflow
```javascript
// Frontend integration
const createClip = async (videoPath, segment) => {
  const response = await fetch('http://localhost:8000/render-clip', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_path: videoPath,
      start_time: segment.start,
      end_time: segment.end,
      crop_mode: 'dynamic'
    })
  });
  
  const result = await response.json();
  return result.output_path;
};
```

## Maintenance

### Logs
Check logs for debugging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Monitoring
- Track processing times for performance optimization
- Monitor disk space in `output/` directory
- Log face detection success rate

---

**Status:** ✅ Implemented (Phases L, M, N, O complete)
**Version:** 1.0.0
**Last Updated:** 2026-01-12
