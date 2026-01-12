"""
Video Renderer Module
Uses FFmpeg to physically crop videos based on analysis data
"""
import subprocess
import os
from typing import List, Dict
import logging
import json

logger = logging.getLogger(__name__)


class VideoRenderer:
    """
    Renders cropped videos using FFmpeg
    """
    
    def __init__(self):
        """Initialize the renderer"""
        # Check if FFmpeg is available
        self._check_ffmpeg()
        logger.info("VideoRenderer initialized")
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is installed and accessible"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("FFmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg not found. Install with: brew install ffmpeg (macOS)")
            raise RuntimeError("FFmpeg is not installed. Please install FFmpeg to use video rendering.")
    
    def render(self, input_path: str, crop_data: List[Dict], output_path: str) -> Dict:
        """
        Render cropped video
        
        Args:
            input_path: Path to input video
            crop_data: List of crop coordinates per frame
            output_path: Path for output video
            
        Returns:
            Dictionary with render results
        """
        if not crop_data:
            raise ValueError("Crop data is empty")
        
        # Get crop dimensions (consistent across frames)
        crop_width = crop_data[0]["width"]
        crop_height = crop_data[0]["height"]
        
        # Strategy: For simplicity, we'll use the average crop position
        # For advanced use case, use FFmpeg's zoompan filter with expressions
        avg_x = int(sum(frame["x"] for frame in crop_data) / len(crop_data))
        avg_y = crop_data[0]["y"]  # Y is typically 0
        
        logger.info(f"Rendering with crop: {crop_width}x{crop_height} at ({avg_x}, {avg_y})")
        
        # Simple approach: Fixed crop position
        success = self._render_simple_crop(
            input_path,
            output_path,
            avg_x,
            avg_y,
            crop_width,
            crop_height
        )
        
        if success:
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            return {
                "success": True,
                "output_path": output_path,
                "crop_width": crop_width,
                "crop_height": crop_height,
                "file_size": file_size,
                "method": "simple_crop"
            }
        else:
            return {
                "success": False,
                "error": "FFmpeg rendering failed"
            }
    
    def _render_simple_crop(
        self,
        input_path: str,
        output_path: str,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> bool:
        """
        Render video with fixed crop position
        
        Args:
            input_path: Input video path
            output_path: Output video path
            x: Crop X position
            y: Crop Y position
            width: Crop width
            height: Crop height
            
        Returns:
            True if successful
        """
        # FFmpeg crop filter: crop=width:height:x:y
        crop_filter = f"crop={width}:{height}:{x}:{y}"
        
        # Build FFmpeg command
        command = [
            "ffmpeg",
            "-i", input_path,
            "-vf", crop_filter,
            "-c:a", "copy",  # Copy audio without re-encoding
            "-y",  # Overwrite output file
            output_path
        ]
        
        try:
            logger.info(f"Running FFmpeg: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("FFmpeg rendering completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            return False
    
    def render_dynamic_crop(
        self,
        input_path: str,
        crop_data: List[Dict],
        output_path: str,
        temp_dir: str = "temp_crop_data"
    ) -> Dict:
        """
        Render video with dynamic crop using zoompan filter
        This is more advanced and creates smooth panning based on frame-by-frame data
        
        Args:
            input_path: Input video path
            crop_data: Frame-by-frame crop data
            output_path: Output video path
            temp_dir: Directory for temporary files
            
        Returns:
            Render result dictionary
        """
        os.makedirs(temp_dir, exist_ok=True)
        
        # Get crop dimensions
        crop_width = crop_data[0]["width"]
        crop_height = crop_data[0]["height"]
        
        # Create expression for dynamic panning
        # FFmpeg zoompan can use frame number (n) in expressions
        # We'll generate a piecewise linear function
        
        # For now, fall back to simple crop
        # TODO: Implement full dynamic crop with zoompan expressions
        logger.warning("Dynamic crop not yet fully implemented, using average position")
        
        return self.render(input_path, crop_data, output_path)


class AdvancedRenderer:
    """
    Advanced rendering with frame-by-frame precision
    Uses OpenCV to manually process each frame (slower but more precise)
    """
    
    def __init__(self):
        import cv2
        self.cv2 = cv2
        logger.info("AdvancedRenderer initialized")
    
    def render_precise(
        self,
        input_path: str,
        crop_data: List[Dict],
        output_path: str
    ) -> Dict:
        """
        Render with frame-by-frame precision using OpenCV
        
        Args:
            input_path: Input video path
            crop_data: Frame-by-frame crop coordinates
            output_path: Output video path
            
        Returns:
            Render result
        """
        cap = self.cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {input_path}")
        
        # Get video properties
        fps = cap.get(self.cv2.CAP_PROP_FPS)
        fourcc = self.cv2.VideoWriter_fourcc(*'mp4v')
        
        crop_width = crop_data[0]["width"]
        crop_height = crop_data[0]["height"]
        
        # Create video writer
        out = self.cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (crop_width, crop_height)
        )
        
        frame_num = 0
        processed_frames = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Get crop coordinates for this frame
                if frame_num < len(crop_data):
                    crop_info = crop_data[frame_num]
                    x = crop_info["x"]
                    y = crop_info["y"]
                    w = crop_info["width"]
                    h = crop_info["height"]
                    
                    # Crop frame
                    cropped = frame[y:y+h, x:x+w]
                    
                    # Write frame
                    out.write(cropped)
                    processed_frames += 1
                
                frame_num += 1
            
            logger.info(f"Processed {processed_frames} frames")
            
        finally:
            cap.release()
            out.release()
        
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        return {
            "success": True,
            "output_path": output_path,
            "processed_frames": processed_frames,
            "file_size": file_size,
            "method": "frame_by_frame"
        }
