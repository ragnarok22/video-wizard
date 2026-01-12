"""
Smart Crop & Video Processing Service
FastAPI application for analyzing and cropping videos
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from pathlib import Path
from typing import Optional
import logging

from analyzer import VideoAnalyzer
from renderer import VideoRenderer
from audio_service import get_audio_service
from config import (
    WHISPER_MODEL, 
    USE_OPENAI_API, 
    OPENAI_API_KEY,
    DEFAULT_TRANSCRIPTION_LANGUAGE
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Video Processing Service",
    description="Smart crop and video processing using AI",
    version="1.0.0"
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize services
analyzer = VideoAnalyzer()
renderer = VideoRenderer()
audio_service = get_audio_service(
    whisper_model=WHISPER_MODEL,
    use_openai_api=USE_OPENAI_API,
    openai_api_key=OPENAI_API_KEY
)


class AnalyzeRequest(BaseModel):
    video_path: str


class AnalyzeResponse(BaseModel):
    video_metadata: dict
    crop_data: list
    smoothed_centers: list


class RenderRequest(BaseModel):
    video_path: str
    crop_data: list
    output_path: Optional[str] = None


class TranscribeRequest(BaseModel):
    video_path: str
    language: Optional[str] = None
    cleanup: Optional[bool] = True


class TranscribeResponse(BaseModel):
    video_path: str
    audio_path: Optional[str]
    segments: list
    full_text: str
    segment_count: int


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Video Processing Service",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file for processing
    """
    try:
        # Validate file type
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Uploaded file: {file.filename}")
        
        return {
            "filename": file.filename,
            "path": str(file_path),
            "message": "File uploaded successfully"
        }
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/analyze-video", response_model=AnalyzeResponse)
async def analyze_video(request: AnalyzeRequest):
    """
    Analyze video and generate crop coordinates for vertical format
    
    Input: Video path (16:9)
    Output: Crop data for 9:16 vertical shorts
    """
    try:
        video_path = request.video_path
        
        # Validate video file exists
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        logger.info(f"Analyzing video: {video_path}")
        
        # Analyze video
        result = analyzer.analyze(video_path)
        
        logger.info(f"Analysis complete. Found {len(result['crop_data'])} frames")
        
        return AnalyzeResponse(**result)
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/render-video")
async def render_video(request: RenderRequest):
    """
    Render cropped video using the analysis data
    """
    try:
        video_path = request.video_path
        crop_data = request.crop_data
        
        # Validate video file
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Generate output path if not provided
        if request.output_path:
            output_path = request.output_path
        else:
            filename = Path(video_path).stem
            output_path = str(OUTPUT_DIR / f"{filename}_cropped.mp4")
        
        logger.info(f"Rendering video: {video_path} -> {output_path}")
        
        # Render video
        result = renderer.render(video_path, crop_data, output_path)
        
        logger.info(f"Rendering complete: {output_path}")
        
        return result
    
    except Exception as e:
        logger.error(f"Rendering error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rendering failed: {str(e)}")


@app.post("/process-video")
async def process_video(request: AnalyzeRequest):
    """
    Complete pipeline: Analyze + Render in one call
    """
    try:
        # First analyze
        analyze_result = await analyze_video(request)
        
        # Then render
        filename = Path(request.video_path).stem
        output_path = str(OUTPUT_DIR / f"{filename}_cropped.mp4")
        
        render_request = RenderRequest(
            video_path=request.video_path,
            crop_data=analyze_result.crop_data,
            output_path=output_path
        )
        
        render_result = await render_video(render_request)
        
        return {
            "analysis": analyze_result.dict(),
            "render": render_result,
            "output_path": output_path
        }
    
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_video(request: TranscribeRequest):
    """
    Extract audio from video and generate timestamped transcription
    
    Input: Video file path
    Output: JSON with transcript segments containing start/end timestamps and text
    
    Example response:
    {
        "video_path": "path/to/video.mp4",
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 4.5,
                "text": "Welcome to this tutorial about NextJS."
            },
            ...
        ],
        "full_text": "Complete transcription...",
        "segment_count": 42
    }
    """
    try:
        video_path = request.video_path
        
        # Validate video file exists
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        logger.info(f"Starting transcription for: {video_path}")
        
        # Run transcription pipeline
        result = audio_service.transcribe_video(
            video_path=video_path,
            language=request.language,
            cleanup=request.cleanup
        )
        
        logger.info(f"Transcription complete. Generated {result['segment_count']} segments")
        
        return TranscribeResponse(**result)
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


        
        render_result = await render_video(render_request)
        
        return {
            "analysis": analyze_result.dict(),
            "render": render_result,
            "output_path": output_path
        }
    
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
