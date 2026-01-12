#!/bin/bash

# Setup script for Video Processing Service

echo "🎬 Video Processing Service Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if FFmpeg is installed
echo ""
echo "Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg is installed"
    ffmpeg -version | head -n 1
else
    echo "⚠️  FFmpeg is not installed"
    echo "Install it with: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux)"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
echo "⚠️  Note: Installing Whisper and PyTorch may take several minutes..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p uploads output temp_crop_data temp

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "import cv2, mediapipe, fastapi, numpy, whisper, torch; print('✅ All Python packages installed successfully')"

if [ $? -ne 0 ]; then
    echo "❌ Some packages failed to import"
    exit 1
fi

# Download Whisper model (optional, will be downloaded on first use)
echo ""
echo "Whisper model will be downloaded automatically on first use."
echo "To pre-download the model, run: python -c 'import whisper; whisper.load_model(\"base\")'"

echo ""
echo "=================================="
echo "✅ Setup completed successfully!"
echo ""
echo "To start the service:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the service: python main.py"
echo "  3. Open http://localhost:8000/docs"
echo ""
