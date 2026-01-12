# Quick Start Guide - Video Processing Service

Get up and running in 5 minutes!

## 🚀 Quick Setup

```bash
# Navigate to the service directory
cd apps/processing-engine

# Run the setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Start the service
python main.py
```

Visit http://localhost:8000/docs for the interactive API documentation.

## 📝 First Request

### Using the Interactive Docs (Recommended)

1. Go to http://localhost:8000/docs
2. Click on `POST /upload` → "Try it out"
3. Select a video file and execute
4. Copy the returned file path
5. Use that path in `POST /analyze-video`

### Using cURL

```bash
# 1. Test health check
curl http://localhost:8000/health

# 2. Upload a video
curl -X POST http://localhost:8000/upload \
  -F "file=@your_video.mp4"

# 3. Analyze (use path from upload response)
curl -X POST http://localhost:8000/analyze-video \
  -H "Content-Type: application/json" \
  -d '{"video_path": "uploads/your_video.mp4"}'

# 4. Complete pipeline (analyze + render)
curl -X POST http://localhost:8000/process-video \
  -H "Content-Type: application/json" \
  -d '{"video_path": "uploads/your_video.mp4"}'

# 5. Transcribe video (audio extraction + speech-to-text)
curl -X POST http://localhost:8000/transcribe \
  -H "Content-Type: application/json" \
  -d '{"video_path": "uploads/your_video.mp4"}'
```

### Using Python Script

```bash
# Run the video processing example
python example_usage.py

# Run the transcription example
python example_transcription.py
```

(Edit the `VIDEO_PATH` variable in the scripts first)

## 🎯 What Videos Work Best?

- **Format**: 16:9 landscape videos (e.g., 1920x1080)
- **Content**: Videos with a person talking (face visible)
- **Duration**: Any length (longer videos take more time to process)
- **Quality**: Higher resolution = better detection

## ⚡ Performance Tips

**Fast Processing** (for testing):
```python
# In analyzer.py, increase sample rate
analyzer = VideoAnalyzer(sample_rate=10)  # Process every 10th frame
```

**High Quality** (for production):
```python
# In analyzer.py, decrease sample rate
analyzer = VideoAnalyzer(sample_rate=3)  # Process every 3rd frame
```

## 🔍 Checking Results

After processing, check the `output/` directory for your cropped videos.

```bash
ls -lh output/
```

## ❓ Common Issues

### "FFmpeg not found"
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
```

### "Module not found"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Cannot open video file"
- Check the file path is correct
- Ensure the file is a valid video format (mp4, mov, avi, etc.)
- Try with a different video file

## 🎓 Next Steps

1. **Customize Settings**: Edit [config.py](config.py) to adjust parameters
2. **API Integration**: See [README.md](README.md) for integration examples
3. **Advanced Features**: Explore the renderer module for frame-by-frame processing

## 📚 Resources

- Full Documentation: [README.md](README.md)
- API Docs: http://localhost:8000/docs
- Example Code: [example_usage.py](example_usage.py)

---

Need help? Check the logs or visit the interactive API docs!
