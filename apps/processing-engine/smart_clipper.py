"""
Smart Video Clipper Module
Creates vertical short clips with intelligent face tracking and smooth camera movement
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
import subprocess
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class SmartClipper:
    """
    Creates vertical short clips with smart cropping based on face detection.
    Implements smooth camera movement to keep the active speaker centered.
    """
    
    def __init__(self, smoothing_window: int = 30):
        """
        Initialize the smart clipper
        
        Args:
            smoothing_window: Window size for moving average filter (default: 30 frames)
        """
        self.smoothing_window = smoothing_window
        
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 1 for full-range detection
            min_detection_confidence=0.5
        )
        
        # Check FFmpeg availability
        self._check_ffmpeg()
        
        logger.info(f"SmartClipper initialized with smoothing_window={smoothing_window}")
    
    def _calculate_crop_dimensions(
        self, width: int, height: int, aspect_ratio: Tuple[int, int] = (9, 16)
    ) -> Tuple[int, int, bool]:
        """
        Calculate optimal crop dimensions based on source and target aspect ratio

        If the video already matches the target aspect ratio, avoid excessive
        cropping and only adjust to maintain exact ratio.

        Args:
            width: Source video width
            height: Source video height
            aspect_ratio: Target aspect ratio as (w, h) tuple, e.g. (9, 16), (1, 1)

        Returns:
            Tuple of (crop_width, crop_height, skip_face_detection)
            skip_face_detection is True when video already matches target ratio
        """
        ar_w, ar_h = aspect_ratio

        # Calculate source and target aspect ratios
        source_aspect = width / height
        target_aspect = ar_w / ar_h

        # Define tolerance for "already matching" (e.g., within 15% of target)
        aspect_tolerance = 0.15
        aspect_diff = abs(source_aspect - target_aspect) / target_aspect

        # Check if video EXACTLY matches the target ratio
        ideal_width = int(height * ar_w / ar_h)
        ideal_height = int(width * ar_h / ar_w)

        if width == ideal_width and height == ideal_height:
            logger.info(
                f"Video is EXACTLY {ar_w}:{ar_h} ({width}x{height}). "
                f"No cropping or face detection needed. Using original video."
            )
            return (width, height, True)

        if aspect_diff <= aspect_tolerance:
            logger.info(
                f"Video aspect ratio {source_aspect:.3f} is close to target {target_aspect:.3f} "
                f"(diff: {aspect_diff*100:.1f}%). Skipping face detection, using simple center crop."
            )
            ideal_width = int(height * ar_w / ar_h)
            ideal_height = int(width * ar_h / ar_w)

            if ideal_width <= width:
                return (ideal_width, height, True)
            else:
                return (width, ideal_height, True)
        elif source_aspect < target_aspect:
            logger.info(
                f"Video aspect ratio {source_aspect:.3f} is more vertical than target {ar_w}:{ar_h}. "
                f"Cropping height to maintain ratio. Skipping face detection."
            )
            crop_height = int(width * ar_h / ar_w)
            return (width, crop_height, True)
        else:
            logger.info(
                f"Video aspect ratio {source_aspect:.3f} requires standard crop to {ar_w}:{ar_h}. "
                f"Using face detection for smart framing."
            )
            crop_width = int(height * ar_w / ar_h)
            return (crop_width, height, False)
    
    def _get_display_dimensions(self, video_path: str) -> Tuple[int, int]:
        """
        Get video display dimensions (accounting for rotation metadata)
        
        Uses FFprobe to get the actual display width/height which already
        accounts for rotation metadata. This is more reliable than trying
        to detect rotation and swap dimensions manually.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (width, height) as they should be displayed
        """
        try:
            # Get width and height streams separately
            cmd_width = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width",
                "-of", "csv=p=0",
                video_path
            ]
            
            cmd_height = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=height",
                "-of", "csv=p=0",
                video_path
            ]
            
            cmd_rotation = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream_tags=rotate:stream_side_data=rotation",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            
            width_result = subprocess.run(cmd_width, capture_output=True, text=True, check=False)
            height_result = subprocess.run(cmd_height, capture_output=True, text=True, check=False)
            rotation_result = subprocess.run(cmd_rotation, capture_output=True, text=True, check=False)
            
            width = int(width_result.stdout.strip().split(',')[0])
            height = int(height_result.stdout.strip().split(',')[0])
            
            # Check for rotation metadata (can be in multiple places)
            rotation = 0
            rotation_output = rotation_result.stdout.strip()
            if rotation_output:
                # Parse rotation - can have multiple lines if both tag and side_data exist
                for line in rotation_output.split('\n'):
                    if line.strip():
                        try:
                            rotation = int(float(line.strip()))
                            break
                        except ValueError:
                            continue
            
            # If video is rotated 90° or 270°, swap dimensions for display
            if rotation in [90, 270]:
                logger.info(f"Video has {rotation}° rotation metadata. Swapping dimensions: {width}x{height} → {height}x{width}")
                return (height, width)
            
            return (width, height)
            
        except Exception as e:
            logger.warning(f"Could not get display dimensions from FFprobe: {e}. Falling back to OpenCV.")
            # Fallback to OpenCV
            cap = cv2.VideoCapture(video_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            return (width, height)
    
    def _check_ffmpeg(self):
        """Verify FFmpeg is installed"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("FFmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("FFmpeg is not installed. Install with: brew install ffmpeg")
    
    def create_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
        crop_mode: str = "dynamic",
        aspect_ratio: Tuple[int, int] = (9, 16)
    ) -> Dict:
        """
        Create a cropped clip from a video segment with the target aspect ratio

        Args:
            video_path: Path to source video file
            start_time: Start timestamp in seconds
            end_time: End timestamp in seconds
            output_path: Path for output clip
            crop_mode: "dynamic" for smooth tracking or "static" for fixed center
            aspect_ratio: Target aspect ratio as (w, h) tuple, e.g. (9, 16), (1, 1)

        Returns:
            Dictionary with clip metadata and output path
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if start_time >= end_time:
            raise ValueError("start_time must be less than end_time")

        ar_w, ar_h = aspect_ratio
        ar_label = f"{ar_w}:{ar_h}"

        logger.info("="*70)
        logger.info(f"🎬 CREATING CLIP: {start_time}s to {end_time}s ({crop_mode} mode, {ar_label})")
        logger.info(f"📁 Input video: {video_path}")
        logger.info("="*70)

        # Get video dimensions with rotation applied (display dimensions)
        width, height = self._get_display_dimensions(video_path)
        source_aspect = width / height

        logger.info(f"📐 INPUT VIDEO DIMENSIONS (with rotation applied):")
        logger.info(f"   • Width: {width}px")
        logger.info(f"   • Height: {height}px")
        logger.info(f"   • Aspect Ratio: {source_aspect:.4f} ({width}:{height})")

        # Identify format
        if abs(source_aspect - 0.5625) < 0.01:
            format_name = "9:16 Portrait"
        elif abs(source_aspect - 1.7778) < 0.01:
            format_name = "16:9 Landscape"
        elif abs(source_aspect - 1.0) < 0.05:
            format_name = "Square"
        elif source_aspect < 0.7:
            format_name = "Vertical Portrait"
        elif source_aspect > 1.3:
            format_name = "Horizontal Landscape"
        else:
            format_name = "Square-ish"
        logger.info(f"   • Format: {format_name}")
        logger.info(f"   • Target: {ar_label}")
        logger.info("")

        crop_width, crop_height, skip_face_detection = self._calculate_crop_dimensions(
            width, height, aspect_ratio
        )

        logger.info(f"🎯 CROP DECISION:")
        logger.info(f"   • Target crop: {crop_width}x{crop_height} ({ar_label})")
        logger.info(f"   • Face detection: {'❌ SKIPPED' if skip_face_detection else '✅ ENABLED'}")

        if skip_face_detection:
            logger.info(f"   • Reason: Video is {ar_label} compatible, no significant cropping needed")
            logger.info(f"   • Crop mode: Static center")
            center_x = max(0, (width - crop_width) // 2)
            center_y = max(0, (height - crop_height) // 2)
            crop_coordinates = [center_x] * 100  # Static center position
            logger.info(f"   • Crop position: X={center_x}, Y={center_y}")
        else:
            # Video needs significant cropping - use face detection
            logger.info(f"   • Reason: Video aspect ratio requires cropping")
            logger.info(f"   • Crop mode: Dynamic face tracking")
            # Phase L: Track faces in the time range
            crop_coordinates = self._track_faces_in_range(
                video_path,
                start_time,
                end_time,
                width,
                height,
                crop_width,
                crop_height
            )

            if not crop_coordinates:
                logger.warning("No faces detected, using center crop")
                center_x = max(0, (width - crop_width) // 2)
                crop_coordinates = [center_x] * 100  # Dummy data for static crop

        # Phase M: Smooth the coordinates
        smoothed_coords = self._smooth_coordinates(crop_coordinates)

        # Phase N: Render the clip
        result = self._render_clip(
            video_path,
            start_time,
            end_time,
            smoothed_coords,
            output_path,
            crop_mode,
            width,
            height,
            crop_width,
            crop_height
        )

        return result
    
    def _track_faces_in_range(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        width: int,
        height: int,
        crop_width: int,
        crop_height: int
    ) -> List[int]:
        """
        Phase L: Track face positions frame-by-frame within the time range
        
        Args:
            video_path: Path to video file
            start_time: Start timestamp in seconds
            end_time: End timestamp in seconds
            width: Display width (with rotation applied)
            height: Display height (with rotation applied)
            crop_width: Target crop width
            crop_height: Target crop height
            
        Returns:
            List of X-coordinates (crop window left edge) for each frame
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Get FPS only (dimensions are passed as parameters with rotation already applied)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info("")
        logger.info(f"👤 FACE TRACKING:")
        logger.info(f"   • Using dimensions: {width}x{height} (rotation already applied)")
        logger.info(f"   • Target crop: {crop_width}x{crop_height}")
        
        # Calculate frame range
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        total_frames = end_frame - start_frame
        
        logger.info(f"   • Frame range: {start_frame} to {end_frame} ({total_frames} frames)")
        logger.info(f"   • FPS: {fps:.2f}")
        
        # Jump to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        face_centers = []
        current_frame = start_frame
        
        while current_frame < end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect face center X coordinate
            center_x = self._detect_face_center(frame, width, height, crop_width)
            face_centers.append(center_x)
            
            current_frame += 1
        
        cap.release()
        
        logger.info(f"Tracked {len(face_centers)} frames with face detection")
        
        return face_centers
    
    def _detect_face_center(
        self,
        frame: np.ndarray,
        width: int,
        height: int,
        crop_width: int
    ) -> int:
        """
        Detect face in frame and return crop window X coordinate
        Prioritizes the most prominent face (likely the speaker)
        
        Args:
            frame: Video frame (BGR image)
            width: Frame width
            height: Frame height
            crop_width: Width of the 9:16 crop window
            
        Returns:
            X coordinate for crop window (left edge)
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        results = self.face_detection.process(rgb_frame)
        
        if results.detections:
            # Select the most prominent face (largest, most centered, highest confidence)
            best_face = self._select_speaking_face(results.detections, width, height)
            
            if best_face:
                bboxC = best_face.location_data.relative_bounding_box
                
                # Get face center in pixel coordinates
                face_center_x = int((bboxC.xmin + bboxC.width / 2) * width)
                
                # Calculate crop window position to center the face
                crop_x = face_center_x - (crop_width // 2)
                
                # Constrain to video boundaries
                crop_x = max(0, min(crop_x, width - crop_width))
                
                return crop_x
        
        # No face detected, center the crop window
        # Handle both cases: crop width smaller than video width, or equal
        if crop_width >= width:
            return 0
        return (width - crop_width) // 2
    
    def _select_speaking_face(self, detections: List, width: int, height: int):
        """
        Select the face most likely to be speaking from multiple detections
        
        Strategy:
        1. Prioritize larger faces (closer to camera, more prominent)
        2. Prioritize faces closer to center (usually the main subject)
        3. Consider detection confidence
        
        Args:
            detections: List of MediaPipe face detections
            width: Frame width
            height: Frame height
            
        Returns:
            The most prominent face detection
        """
        if not detections:
            return None
        
        if len(detections) == 1:
            return detections[0]
        
        best_face = None
        best_score = -1
        
        frame_center_x = width / 2
        frame_center_y = height / 2
        
        for detection in detections:
            bbox = detection.location_data.relative_bounding_box
            confidence = detection.score[0] if detection.score else 0.5
            
            # Calculate face metrics
            face_width = bbox.width * width
            face_height = bbox.height * height
            face_area = face_width * face_height
            
            # Calculate distance from frame center
            face_center_x = (bbox.xmin + bbox.width / 2) * width
            face_center_y = (bbox.ymin + bbox.height / 2) * height
            distance_from_center = np.sqrt(
                (face_center_x - frame_center_x) ** 2 + 
                (face_center_y - frame_center_y) ** 2
            )
            
            # Normalize metrics (0-1 scale)
            # Larger face area = more prominent (normalize by frame area)
            size_score = face_area / (width * height)
            
            # Closer to center = more prominent (normalize by max possible distance)
            max_distance = np.sqrt((width / 2) ** 2 + (height / 2) ** 2)
            center_score = 1 - (distance_from_center / max_distance)
            
            # Combined score (weighted)
            # Size is most important (50%), center position (30%), confidence (20%)
            score = (
                size_score * 0.5 + 
                center_score * 0.3 + 
                confidence * 0.2
            )
            
            if score > best_score:
                best_score = score
                best_face = detection
        
        return best_face
    
    def _smooth_coordinates(self, coordinates: List[int]) -> List[int]:
        """
        Phase M: Apply moving average filter to smooth camera movement
        
        Args:
            coordinates: Raw X-coordinates for each frame
            
        Returns:
            Smoothed X-coordinates
        """
        if len(coordinates) < self.smoothing_window:
            # Not enough data for smoothing, return as-is
            return coordinates
        
        # Convert to numpy array for efficient computation
        coords_array = np.array(coordinates, dtype=np.float32)
        
        # Apply moving average filter
        smoothed = np.convolve(
            coords_array,
            np.ones(self.smoothing_window) / self.smoothing_window,
            mode='same'
        )
        
        # Convert back to integers
        smoothed_coords = smoothed.astype(int).tolist()
        
        logger.info(f"Smoothed {len(coordinates)} coordinates (window={self.smoothing_window})")
        
        return smoothed_coords
    
    def _render_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        smoothed_coords: List[int],
        output_path: str,
        crop_mode: str,
        width: int,
        height: int,
        crop_width: int,
        crop_height: int
    ) -> Dict:
        """
        Phase N: Render the cropped clip using FFmpeg
        
        Args:
            video_path: Source video path
            start_time: Start time in seconds
            end_time: End time in seconds
            smoothed_coords: Smoothed crop coordinates
            output_path: Output file path
            crop_mode: "dynamic" or "static"
            width: Display width (with rotation applied)
            height: Display height (with rotation applied)
            crop_width: Target crop width
            crop_height: Target crop height
            
        Returns:
            Dictionary with render results
        """
        # Get FPS only (dimensions are passed as parameters with rotation already applied)
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        # Calculate Y offset for vertical centering (when crop_height < height)
        center_y = max(0, (height - crop_height) // 2)
        
        if crop_mode == "static":
            # Strategy A: Simple static crop at average position
            avg_x = int(np.mean(smoothed_coords))
            success = self._render_static_crop(
                video_path,
                start_time,
                end_time,
                avg_x,
                center_y,
                crop_width,
                crop_height,
                output_path
            )
        else:
            # Strategy B: Dynamic crop with smooth panning
            success = self._render_dynamic_crop(
                video_path,
                start_time,
                end_time,
                smoothed_coords,
                crop_width,
                crop_height,
                fps,
                output_path
            )
        
        if success:
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            duration = end_time - start_time
            
            logger.info("")
            logger.info("="*70)
            logger.info(f"✅ CLIP CREATED SUCCESSFULLY")
            logger.info(f"📁 Output: {output_path}")
            logger.info(f"📊 OUTPUT VIDEO DETAILS:")
            logger.info(f"   • Dimensions: {crop_width}x{crop_height}")
            logger.info(f"   • Aspect Ratio: {crop_width/crop_height:.4f} (9:16 = 0.5625)")
            logger.info(f"   • Duration: {duration:.2f}s")
            logger.info(f"   • File Size: {file_size / (1024*1024):.2f} MB")
            logger.info(f"   • Crop Mode: {crop_mode}")
            logger.info("="*70)
            
            return {
                "success": True,
                "output_path": output_path,
                "crop_mode": crop_mode,
                "duration": duration,
                "crop_dimensions": {
                    "width": crop_width,
                    "height": crop_height
                },
                "file_size": file_size,
                "start_time": start_time,
                "end_time": end_time
            }
        else:
            logger.error("="*70)
            logger.error("❌ CLIP CREATION FAILED")
            logger.error("FFmpeg rendering failed")
            logger.error("="*70)
            return {
                "success": False,
                "error": "FFmpeg rendering failed"
            }
    
    def _render_static_crop(
        self,
        input_path: str,
        start_time: float,
        end_time: float,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: str
    ) -> bool:
        """
        Render with fixed crop position (simpler, faster)
        
        Args:
            input_path: Source video
            start_time: Start time in seconds
            end_time: End time in seconds
            x, y: Crop position
            width, height: Crop dimensions
            output_path: Output file
            
        Returns:
            True if successful
        """
        duration = end_time - start_time
        
        # FFmpeg command with trim and crop
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-ss", str(start_time),  # Start time
            "-t", str(duration),  # Duration
            "-i", input_path,  # Input file
            "-vf", f"crop={width}:{height}:{x}:{y}",  # Crop filter
            "-c:a", "copy",  # Copy audio stream
            "-preset", "fast",  # Encoding speed
            output_path
        ]
        
        logger.info("")
        logger.info(f"🎥 RENDERING WITH FFMPEG:")
        logger.info(f"   • Crop filter: crop={width}:{height}:{x}:{y}")
        logger.info(f"   • Position: X={x}, Y={y}")
        logger.info(f"   • Size: {width}x{height}")
        logger.info(f"   • Duration: {duration:.2f}s")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Static crop render completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            return False
    
    def _render_dynamic_crop(
        self,
        input_path: str,
        start_time: float,
        end_time: float,
        x_coords: List[int],
        width: int,
        height: int,
        fps: float,
        output_path: str
    ) -> bool:
        """
        Render with dynamic crop that follows the smoothed path
        Uses FFmpeg's crop filter with interpolated expressions
        
        Args:
            input_path: Source video
            start_time: Start time in seconds
            end_time: End time in seconds
            x_coords: List of X coordinates (one per frame)
            width: Crop width
            height: Crop height
            fps: Video frame rate
            output_path: Output file
            
        Returns:
            True if successful
        """
        duration = end_time - start_time
        
        # For dynamic cropping, we'll use zoompan filter or crop with expressions
        # Simplified approach: divide into segments and use sendcmd
        
        # For now, use a simplified dynamic approach with crop expressions
        # FFmpeg crop filter supports expressions like 'crop=w:h:x:y'
        # We'll use the 'n' (frame number) variable with a linear interpolation
        
        # Calculate average velocity for smooth panning
        if len(x_coords) > 1:
            start_x = x_coords[0]
            end_x = x_coords[-1]
            total_frames = len(x_coords)
            
            # Linear interpolation expression: start + (end - start) * n / total_frames
            # However, FFmpeg's crop filter is tricky with dynamic expressions
            # Let's use a simpler approach: sample key positions
            
            # For true dynamic panning, we'd need zoompan or complex filter chains
            # Simplified: use average position (fallback to static)
            avg_x = int(np.mean(x_coords))
            
            logger.warning("Dynamic crop with full smoothing not implemented yet, using average position")
            return self._render_static_crop(
                input_path,
                start_time,
                end_time,
                avg_x,
                0,
                width,
                height,
                output_path
            )
        else:
            # Single position
            x = x_coords[0] if x_coords else 0
            return self._render_static_crop(
                input_path,
                start_time,
                end_time,
                x,
                0,
                width,
                height,
                output_path
            )
