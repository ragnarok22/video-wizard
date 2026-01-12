"""
Example usage of the Audio Transcription API

This script demonstrates how to use the /transcribe endpoint
to extract audio from a video and generate timestamped transcriptions.

The service now uses OpenAI API by default for better Spanish transcription.
Set OPENAI_API_KEY environment variable before running.
"""
import requests
import json
import os

# API endpoint
BASE_URL = "http://localhost:8000"

# Check if OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  Warning: OPENAI_API_KEY not set. Add it to your .env file:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print()

def transcribe_video_example():
    """
    Example: Transcribe a video file
    """
    print("=" * 60)
    print("Audio Transcription Example")
    print("=" * 60)
    
    # Request payload
    payload = {
        "video_path": "uploads/sample_video.mp4",  # Update with your video path
        "language": None,  # Auto-detect language, or specify "en", "es", etc.
        "cleanup": True    # Delete temporary audio file after transcription
    }
    
    print(f"\n1. Sending transcription request...")
    print(f"   Video: {payload['video_path']}")
    
    try:
        # Make API request
        response = requests.post(
            f"{BASE_URL}/transcribe",
            json=payload,
            timeout=300  # 5 minutes timeout for large videos
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n2. Transcription Complete!")
            print(f"   Total segments: {result['segment_count']}")
            print(f"   Video: {result['video_path']}")
            
            print(f"\n3. First 5 segments:")
            print("-" * 60)
            for segment in result['segments'][:5]:
                print(f"   [{segment['start']:.2f}s - {segment['end']:.2f}s]")
                print(f"   {segment['text']}")
                print()
            
            print(f"\n4. Full Text Preview (first 200 chars):")
            print("-" * 60)
            print(f"   {result['full_text'][:200]}...")
            
            # Save full results to file
            output_file = "transcription_output.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n5. Full transcription saved to: {output_file}")
            
        else:
            print(f"\nError: {response.status_code}")
            print(f"Details: {response.text}")
    
    except requests.exceptions.Timeout:
        print("\nError: Request timed out. Video might be too large.")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server. Is it running?")
        print("Start server with: python main.py")
    except Exception as e:
        print(f"\nError: {str(e)}")


def check_service_health():
    """Check if the service is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ Service is running at {BASE_URL}")
            return True
        else:
            print(f"✗ Service returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Service is not running at {BASE_URL}")
        print("  Start with: python main.py")
        return False


if __name__ == "__main__":
    print("\nChecking service status...")
    if check_service_health():
        print("\nRunning transcription example...")
        transcribe_video_example()
    else:
        print("\nPlease start the service first:")
        print("  cd apps/processing-engine")
        print("  python main.py")
