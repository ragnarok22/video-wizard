"""
Example usage script for the Video Processing Service
Demonstrates how to use the API programmatically
"""
import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
VIDEO_PATH = "test_video.mp4"  # Change to your test video path


def check_health():
    """Check if the service is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def upload_video(file_path: str):
    """Upload a video file"""
    print(f"📤 Uploading video: {file_path}")
    
    with open(file_path, "rb") as f:
        response = requests.post(
            f"{API_BASE_URL}/upload",
            files={"file": (Path(file_path).name, f, "video/mp4")}
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload successful: {result['filename']}")
        return result["path"]
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return None


def analyze_video(video_path: str):
    """Analyze video and get crop data"""
    print(f"\n🔍 Analyzing video: {video_path}")
    
    start_time = time.time()
    
    response = requests.post(
        f"{API_BASE_URL}/analyze-video",
        json={"video_path": video_path}
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        metadata = result["video_metadata"]
        
        print(f"✅ Analysis complete in {elapsed:.2f}s")
        print(f"   Video: {metadata['width']}x{metadata['height']}, {metadata['duration']:.2f}s")
        print(f"   Crop: {metadata['crop_width']}x{metadata['crop_height']}")
        print(f"   Frames analyzed: {len(result['crop_data'])}")
        
        return result
    else:
        print(f"❌ Analysis failed: {response.status_code}")
        print(response.text)
        return None


def render_video(video_path: str, crop_data: list, output_path: str = None):
    """Render cropped video"""
    print(f"\n🎬 Rendering cropped video...")
    
    start_time = time.time()
    
    payload = {
        "video_path": video_path,
        "crop_data": crop_data
    }
    
    if output_path:
        payload["output_path"] = output_path
    
    response = requests.post(
        f"{API_BASE_URL}/render-video",
        json=payload
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Rendering complete in {elapsed:.2f}s")
        print(f"   Output: {result['output_path']}")
        print(f"   File size: {result['file_size'] / 1024 / 1024:.2f} MB")
        return result
    else:
        print(f"❌ Rendering failed: {response.status_code}")
        print(response.text)
        return None


def process_video_complete(video_path: str):
    """Complete pipeline: analyze + render"""
    print(f"\n🚀 Processing video (complete pipeline): {video_path}")
    
    start_time = time.time()
    
    response = requests.post(
        f"{API_BASE_URL}/process-video",
        json={"video_path": video_path}
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Complete processing done in {elapsed:.2f}s")
        print(f"   Output: {result['output_path']}")
        return result
    else:
        print(f"❌ Processing failed: {response.status_code}")
        print(response.text)
        return None


def main():
    """Main example workflow"""
    print("🎬 Video Processing Service - Example Usage")
    print("=" * 50)
    
    # Check if service is running
    if not check_health():
        print("❌ Service is not running. Start it with: python main.py")
        return
    
    print("✅ Service is running\n")
    
    # Check if test video exists
    if not Path(VIDEO_PATH).exists():
        print(f"❌ Test video not found: {VIDEO_PATH}")
        print("Please provide a valid video file path")
        return
    
    # Method 1: Step by step (upload, analyze, render)
    print("\n📋 Method 1: Step-by-step processing")
    print("-" * 50)
    
    # Upload
    uploaded_path = upload_video(VIDEO_PATH)
    if not uploaded_path:
        return
    
    # Analyze
    analysis = analyze_video(uploaded_path)
    if not analysis:
        return
    
    # Save analysis to file (optional)
    with open("analysis_result.json", "w") as f:
        json.dump(analysis, f, indent=2)
    print("💾 Analysis saved to: analysis_result.json")
    
    # Render
    render_result = render_video(
        uploaded_path,
        analysis["crop_data"],
        output_path="output/cropped_step_by_step.mp4"
    )
    
    # Method 2: Complete pipeline in one call
    print("\n\n📋 Method 2: Complete pipeline")
    print("-" * 50)
    
    result = process_video_complete(uploaded_path)
    
    print("\n" + "=" * 50)
    print("✅ Example completed successfully!")
    print("\nCheck the 'output/' directory for rendered videos")


if __name__ == "__main__":
    main()
