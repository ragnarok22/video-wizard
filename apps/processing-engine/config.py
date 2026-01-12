"""
Configuration settings for the Video Processing Service
"""
import os
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp_crop_data"
AUDIO_TEMP_DIR = BASE_DIR / "temp"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
AUDIO_TEMP_DIR.mkdir(exist_ok=True)

# Video Analysis Settings
SAMPLE_RATE = 5  # Process every Nth frame
MIN_DETECTION_CONFIDENCE = 0.5  # Face detection confidence threshold
SMOOTHING_WINDOW_SIZE = 15  # Moving average window size

# Video Processing Settings
TARGET_ASPECT_RATIO = (9, 16)  # Output aspect ratio (width, height)
DEFAULT_QUALITY = "high"  # Video encoding quality

# Audio & Transcription Settings
USE_OPENAI_API = os.getenv("USE_OPENAI_API", "true").lower() == "true"  # Use OpenAI API instead of local Whisper
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Required if USE_OPENAI_API=True
WHISPER_MODEL = "base"  # Local Whisper model: "tiny", "base", "small", "medium", "large" (only if USE_OPENAI_API=False)
DEFAULT_TRANSCRIPTION_LANGUAGE = "es"  # Default language for transcription (Spanish)
AUDIO_FORMAT = "wav"  # Output audio format: "wav" or "mp3"
AUDIO_SAMPLE_RATE = 16000  # Sample rate in Hz (16kHz optimal for Whisper)
AUDIO_BITRATE = "128k"  # Bitrate for MP3 format

# API Settings
API_TITLE = "Video Processing Service"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Smart crop and video processing using AI"

# CORS Settings
CORS_ORIGINS = ["*"]  # Configure for production

# Logging
LOG_LEVEL = "INFO"
