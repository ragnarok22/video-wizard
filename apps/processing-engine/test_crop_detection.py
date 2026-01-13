#!/usr/bin/env python3
"""
Test script to verify video crop detection logic
Place your 9:16 video in the temp/ folder and run this script
"""
import cv2
import subprocess
import sys
from pathlib import Path


def get_opencv_dimensions(video_path):
    """Get dimensions using OpenCV (raw, no rotation)"""
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height


def get_ffprobe_info(video_path):
    """Get video info using FFprobe"""
    try:
        # Get width
        cmd_width = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width", "-of", "csv=p=0", video_path
        ]
        width_result = subprocess.run(cmd_width, capture_output=True, text=True, check=False)
        width = int(width_result.stdout.strip().replace(',', ''))
        
        # Get height
        cmd_height = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=height", "-of", "csv=p=0", video_path
        ]
        height_result = subprocess.run(cmd_height, capture_output=True, text=True, check=False)
        height = int(height_result.stdout.strip().replace(',', ''))
        
        # Get rotation
        cmd_rotation = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream_tags=rotate:stream_side_data=rotation",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        rotation_result = subprocess.run(cmd_rotation, capture_output=True, text=True, check=False)
        rotation = 0
        rotation_output = rotation_result.stdout.strip()
        if rotation_output:
            # Parse rotation - can have multiple lines
            for line in rotation_output.split('\n'):
                if line.strip():
                    try:
                        rotation = int(float(line.strip()))
                        break
                    except ValueError:
                        continue
        
        # Get all stream info (raw dump)
        cmd_all = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream", "-of", "json", video_path
        ]
        all_result = subprocess.run(cmd_all, capture_output=True, text=True, check=False)
        
        return width, height, rotation, all_result.stdout
        
    except Exception as e:
        print(f"❌ Error getting FFprobe info: {e}")
        return None, None, None, None


def calculate_display_dimensions(width, height, rotation):
    """Calculate display dimensions accounting for rotation"""
    if rotation in [90, 270]:
        print(f"🔄 Rotation detected: {rotation}°. Swapping dimensions.")
        return height, width
    return width, height


def should_skip_crop(width, height):
    """Determine if crop should be skipped (video is already 9:16)"""
    source_aspect = width / height
    target_aspect = 9 / 16  # 0.5625
    aspect_tolerance = 0.15
    aspect_diff = abs(source_aspect - target_aspect) / target_aspect
    
    # Check if exactly 9:16
    ideal_width = int(height * 9 / 16)
    ideal_height = int(width * 16 / 9)
    
    if width == ideal_width:
        return True, "EXACTLY 9:16", aspect_diff
    
    if aspect_diff <= aspect_tolerance:
        return True, f"Within {aspect_tolerance*100}% tolerance", aspect_diff
    
    return False, "Requires cropping", aspect_diff


def main():
    print("=" * 70)
    print("VIDEO CROP DETECTION TEST")
    print("=" * 70)
    
    # Find video in temp folder
    temp_dir = Path("temp")
    if not temp_dir.exists():
        temp_dir.mkdir()
        print(f"\n❌ Created temp/ folder. Please place your 9:16 video there and run again.")
        return
    
    videos = list(temp_dir.glob("*.mp4")) + list(temp_dir.glob("*.mov"))
    
    if not videos:
        print(f"\n❌ No videos found in temp/ folder")
        print(f"   Place your 9:16 video in: {temp_dir.absolute()}")
        return
    
    video_path = str(videos[0])
    print(f"\n📹 Testing video: {video_path}")
    print(f"   File size: {Path(video_path).stat().st_size / (1024*1024):.2f} MB")
    
    # Test 1: OpenCV dimensions (raw)
    print(f"\n{'─' * 70}")
    print("TEST 1: OpenCV Dimensions (raw, ignores rotation)")
    print(f"{'─' * 70}")
    cv_width, cv_height = get_opencv_dimensions(video_path)
    print(f"Width:  {cv_width}px")
    print(f"Height: {cv_height}px")
    print(f"Aspect: {cv_width/cv_height:.4f}")
    
    # Test 2: FFprobe info
    print(f"\n{'─' * 70}")
    print("TEST 2: FFprobe Information")
    print(f"{'─' * 70}")
    ff_width, ff_height, rotation, raw_info = get_ffprobe_info(video_path)
    
    if ff_width is None:
        print("❌ FFprobe failed. Cannot continue.")
        return
    
    print(f"Width:    {ff_width}px")
    print(f"Height:   {ff_height}px")
    print(f"Rotation: {rotation}°")
    print(f"Aspect:   {ff_width/ff_height:.4f}")
    
    # Test 3: Display dimensions (with rotation)
    print(f"\n{'─' * 70}")
    print("TEST 3: Display Dimensions (accounting for rotation)")
    print(f"{'─' * 70}")
    display_width, display_height = calculate_display_dimensions(ff_width, ff_height, rotation)
    display_aspect = display_width / display_height
    print(f"Width:  {display_width}px")
    print(f"Height: {display_height}px")
    print(f"Aspect: {display_aspect:.4f}")
    print(f"Target: {9/16:.4f} (9:16)")
    
    # Test 4: Crop decision
    print(f"\n{'─' * 70}")
    print("TEST 4: Crop Decision")
    print(f"{'─' * 70}")
    skip_crop, reason, aspect_diff = should_skip_crop(display_width, display_height)
    
    print(f"Should skip crop: {'✅ YES' if skip_crop else '❌ NO'}")
    print(f"Reason: {reason}")
    print(f"Aspect difference: {aspect_diff*100:.2f}%")
    print(f"Tolerance: 15%")
    
    if skip_crop:
        print(f"\n✅ VIDEO IS 9:16 COMPATIBLE - NO CROPPING NEEDED")
    else:
        print(f"\n❌ VIDEO REQUIRES CROPPING")
        ideal_width = int(display_height * 9 / 16)
        print(f"   Will crop from {display_width}x{display_height} to {ideal_width}x{display_height}")
    
    # Test 5: Raw FFprobe dump
    print(f"\n{'─' * 70}")
    print("TEST 5: Raw FFprobe Stream Info")
    print(f"{'─' * 70}")
    print(raw_info)
    
    print(f"\n{'=' * 70}")
    print("TEST COMPLETE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
