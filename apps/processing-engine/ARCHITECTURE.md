# Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  (Web App / cURL / Python Script / Direct API)                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                        │
│                         (main.py)                               │
│                                                                 │
│  Endpoints:                                                     │
│  • POST /upload          → File handling                        │
│  • POST /analyze-video   → Analysis coordination               │
│  • POST /render-video    → Rendering coordination              │
│  • POST /process-video   → Complete pipeline                   │
│  • GET  /health          → Health check                         │
└──────────┬────────────────────────────┬─────────────────────────┘
           │                            │
           │                            │
           ▼                            ▼
┌─────────────────────────┐   ┌────────────────────────┐
│   VIDEO ANALYZER        │   │   VIDEO RENDERER       │
│    (analyzer.py)        │   │    (renderer.py)       │
│                         │   │                        │
│ • Load video (OpenCV)   │   │ • FFmpeg wrapper       │
│ • Sample frames         │   │ • Crop execution       │
│ • Face detection        │   │ • Audio preservation   │
│ • Position smoothing    │   │ • Format conversion    │
│ • Crop calculation      │   │ • File output          │
└─────────┬───────────────┘   └───────────┬────────────┘
          │                               │
          │ Uses                          │ Uses
          ▼                               ▼
┌─────────────────────────┐   ┌────────────────────────┐
│      MEDIAPIPE          │   │       FFMPEG           │
│   Face Detection        │   │   Video Processing     │
│  (BlazeFace Model)      │   │                        │
└─────────────────────────┘   └────────────────────────┘
```

---

## Data Flow Diagram

### Complete Processing Pipeline

```
┌─────────────┐
│ Input Video │ (16:9 Landscape, e.g., 1920x1080)
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  1. VIDEO LOADING    │
│  • OpenCV capture    │
│  • Get properties    │
│  • Calculate target  │
│    crop size (9:16)  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  2. FRAME SAMPLING   │
│  • Every 5th frame   │
│  • Convert to RGB    │
│  • Pass to detector  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  3. FACE DETECTION   │
│  • MediaPipe process │
│  • Get bounding box  │
│  • Calculate center  │
│  • Fallback to frame │
│    center if no face │
└──────┬───────────────┘
       │
       │ Face Centers: [960, 965, 955, 970, ...]
       │
       ▼
┌──────────────────────┐
│  4. SMOOTHING        │
│  • Moving average    │
│    (window size: 15) │
│  • Edge handling     │
│  • Output smooth     │
│    trajectory        │
└──────┬───────────────┘
       │
       │ Smoothed: [960, 962, 963, 965, ...]
       │
       ▼
┌──────────────────────┐
│  5. INTERPOLATION    │
│  • Fill all frames   │
│  • Linear interp     │
│  • Generate crop     │
│    coordinates       │
└──────┬───────────────┘
       │
       │ Crop Data: [
       │   {frame: 0, x: 656, y: 0, w: 607, h: 1080},
       │   {frame: 1, x: 657, y: 0, w: 607, h: 1080},
       │   ...
       │ ]
       │
       ▼
┌──────────────────────┐
│  6. BOUNDARY CHECK   │
│  • Ensure x >= 0     │
│  • Ensure x+w <= W   │
│  • Clamp values      │
└──────┬───────────────┘
       │
       │ Valid Crop Data
       │
       ▼
┌──────────────────────┐
│  7. VIDEO RENDERING  │
│  • FFmpeg crop cmd   │
│  • Audio copy        │
│  • H.264 encoding    │
└──────┬───────────────┘
       │
       ▼
┌─────────────┐
│ Output Video│ (9:16 Portrait, e.g., 607x1080)
└─────────────┘
```

---

## Component Interaction Sequence

### Scenario: User uploads and processes a video

```
┌──────┐          ┌─────────┐        ┌──────────┐      ┌──────────┐
│Client│          │FastAPI  │        │Analyzer  │      │Renderer  │
└──┬───┘          └────┬────┘        └────┬─────┘      └────┬─────┘
   │                   │                  │                 │
   │ POST /upload      │                  │                 │
   ├──────────────────>│                  │                 │
   │                   │                  │                 │
   │ 200 {path}        │                  │                 │
   │<──────────────────┤                  │                 │
   │                   │                  │                 │
   │ POST /process-video                  │                 │
   ├──────────────────>│                  │                 │
   │                   │                  │                 │
   │                   │ analyze(path)    │                 │
   │                   ├─────────────────>│                 │
   │                   │                  │                 │
   │                   │                  │ [Load video]    │
   │                   │                  │ [Detect faces]  │
   │                   │                  │ [Smooth]        │
   │                   │                  │ [Generate data] │
   │                   │                  │                 │
   │                   │ {metadata, crop} │                 │
   │                   │<─────────────────┤                 │
   │                   │                  │                 │
   │                   │ render(path, crop)                 │
   │                   ├───────────────────────────────────>│
   │                   │                  │                 │
   │                   │                  │   [FFmpeg crop] │
   │                   │                  │   [Encode]      │
   │                   │                  │                 │
   │                   │      {output_path}                 │
   │                   │<───────────────────────────────────┤
   │                   │                  │                 │
   │ 200 {result}      │                  │                 │
   │<──────────────────┤                  │                 │
   │                   │                  │                 │
```

---

## File System Layout

```
/apps/processing-engine/
│
├── [Code Files]
│   ├── main.py           → Entry point, API routes
│   ├── analyzer.py       → Analysis logic
│   ├── renderer.py       → Rendering logic
│   └── config.py         → Configuration
│
├── [Documentation]
│   ├── README.md         → Full docs
│   ├── QUICKSTART.md     → Quick start
│   ├── IMPLEMENTATION_SUMMARY.md → This summary
│   └── ARCHITECTURE.md   → This file
│
├── [Configuration]
│   ├── requirements.txt  → Python deps
│   ├── package.json      → npm scripts
│   ├── Dockerfile        → Container config
│   └── docker-compose.yml → Orchestration
│
├── [Development]
│   ├── setup.sh          → Setup script
│   ├── example_usage.py  → Examples
│   ├── test_service.py   → Tests
│   └── .gitignore        → Git rules
│
└── [Runtime Directories] (auto-created)
    ├── uploads/          → Uploaded videos
    ├── output/           → Processed videos
    ├── temp_crop_data/   → Temporary files
    └── venv/             → Python virtual env
```

---

## Technology Stack Layers

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                   │
│  FastAPI Routes • Swagger UI • RESTful API              │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                 │
│  VideoAnalyzer • VideoRenderer • Pipeline Orchestration │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                    PROCESSING LAYER                     │
│  MediaPipe (Face Detection) • NumPy (Math/Smoothing)    │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                    I/O LAYER                            │
│  OpenCV (Video I/O) • FFmpeg (Encoding) • File System   │
└─────────────────────────────────────────────────────────┘
```

---

## Algorithms Deep Dive

### 1. Moving Average Smoothing

```
Input:  [100, 105, 98, 102, 101, 103, 99, 100]
Window: 3

Process:
  Index 0: avg([100])           = 100.0
  Index 1: avg([100, 105])      = 102.5
  Index 2: avg([100, 105, 98])  = 101.0
  Index 3: avg([105, 98, 102])  = 101.7
  Index 4: avg([98, 102, 101])  = 100.3
  Index 5: avg([102, 101, 103]) = 102.0
  Index 6: avg([101, 103, 99])  = 101.0
  Index 7: avg([103, 99, 100])  = 100.7

Output: [100.0, 102.5, 101.0, 101.7, 100.3, 102.0, 101.0, 100.7]
```

### 2. Crop Position Calculation

```python
# Given:
frame_width = 1920 (px)
frame_height = 1080 (px)
face_center_x = 960 (px)
target_aspect = 9/16

# Calculate:
crop_width = height × (9/16) = 1080 × 0.5625 = 607 (px)
crop_height = height = 1080 (px)

# Center crop on face:
crop_x = face_center_x - (crop_width / 2)
       = 960 - 303.5
       = 656.5 → 656 (px)

# Constrain to boundaries:
crop_x = max(0, min(crop_x, frame_width - crop_width))
       = max(0, min(656, 1920 - 607))
       = max(0, min(656, 1313))
       = 656 (px) ✓

# Result:
crop_region = [x: 656, y: 0, w: 607, h: 1080]
```

---

## Performance Optimization Strategies

### 1. Frame Sampling
```
Instead of processing 1800 frames (60s @ 30fps):
Process 360 frames (every 5th)
↓
6x faster analysis
```

### 2. Detection Model Selection
```
MediaPipe BlazeFace:
• Model: full-range (1)
• Confidence: 0.5
• Trade-off: Speed vs Accuracy
```

### 3. FFmpeg Efficiency
```
Audio: Copy without re-encoding
Video: Hardware acceleration (when available)
Filter: Single-pass crop operation
```

---

## Error Handling Flow

```
┌─────────────┐
│ API Request │
└──────┬──────┘
       │
       ▼
┌──────────────┐     No      ┌─────────────┐
│ File Exists? ├────────────>│ 404 Error   │
└──────┬───────┘             └─────────────┘
       │ Yes
       ▼
┌──────────────┐     Fail    ┌─────────────┐
│ Video Valid? ├────────────>│ 400 Error   │
└──────┬───────┘             └─────────────┘
       │ Pass
       ▼
┌──────────────┐     Error   ┌─────────────┐
│ Process      ├────────────>│ 500 Error   │
└──────┬───────┘             │ + Log       │
       │ Success             └─────────────┘
       ▼
┌──────────────┐
│ 200 Response │
└──────────────┘
```

---

## Deployment Architectures

### 1. Local Development
```
[Developer Machine]
    ├── Python venv
    ├── FFmpeg (system)
    └── FastAPI (port 8000)
```

### 2. Docker Container
```
[Docker Container]
    ├── Python 3.11
    ├── FFmpeg
    ├── App code
    └── Volume mounts
        ├── /uploads
        └── /output
```

### 3. Production (Future)
```
[Load Balancer]
    │
    ├── [Container 1] ─┐
    ├── [Container 2] ─┼─> [Shared Storage]
    └── [Container 3] ─┘     (S3/NFS)
         │
         └─> [Message Queue]
              (Redis/RabbitMQ)
```

---

## Integration Points

### With Frontend (Next.js)
```typescript
// Upload from browser
const file = document.getElementById('videoInput').files[0];
await uploadVideo(file);

// Process
const result = await processVideo(uploadPath);

// Display result
<video src={result.output_path} />
```

### With Other Services
```python
# Webhook notification
requests.post('https://notify-service/webhook', {
    'event': 'video_processed',
    'video_id': '123',
    'output_url': 'https://cdn/video.mp4'
})
```

---

## Monitoring & Observability

### Metrics to Track (Future)
- Request rate (req/min)
- Processing time (seconds)
- Error rate (%)
- Queue depth
- Resource usage (CPU/Memory)
- Video sizes (input/output)

### Logging Levels
```
INFO:  Normal operations
WARN:  Recoverable issues (no face detected)
ERROR: Processing failures
DEBUG: Detailed diagnostics
```

---

## Summary

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Modular, testable components
- ✅ Clear data flow
- ✅ Scalability potential
- ✅ Multiple deployment options
- ✅ Comprehensive error handling

Built for reliability, performance, and maintainability.
