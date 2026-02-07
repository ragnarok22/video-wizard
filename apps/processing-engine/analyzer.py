"""
Video Analyzer Module
Uses MediaPipe and OpenCV to detect faces and calculate crop coordinates
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """
    Analyzes video to find optimal crop window for a target aspect ratio.
    Tracks faces and smooths camera movement.
    """
    
    def __init__(self, sample_rate: int = 5):
        """
        Initialize the analyzer
        
        Args:
            sample_rate: Process every Nth frame (default: 5 for performance)
        """
        self.sample_rate = sample_rate
        
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for short-range, 1 for full-range
            min_detection_confidence=0.5
        )
        
        logger.info("VideoAnalyzer initialized")
    
    def analyze(self, video_path: str, aspect_ratio: Tuple[int, int] = (9, 16)) -> Dict:
        """
        Analyze video and generate crop data for the given aspect ratio

        Args:
            video_path: Path to input video file
            aspect_ratio: Target aspect ratio as (w, h) tuple, e.g. (9, 16), (1, 1)

        Returns:
            Dictionary containing video metadata and crop coordinates
        """
        ar_w, ar_h = aspect_ratio

        # Open video
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        logger.info(f"Video: {width}x{height}, {fps} fps, {total_frames} frames, {duration:.2f}s")

        # Calculate target crop dimensions for the requested aspect ratio
        crop_width = int(height * ar_w / ar_h)
        crop_height = height

        # If crop_width exceeds video width, crop height instead
        if crop_width > width:
            crop_width = width
            crop_height = int(width * ar_h / ar_w)

        logger.info(f"Target crop size: {crop_width}x{crop_height} ({ar_w}:{ar_h})")
        
        # Detect faces and track centers
        face_centers = []
        frame_numbers = []
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process only sampled frames
            if frame_count % self.sample_rate == 0:
                center_x = self._detect_face_center(frame, width, height)
                face_centers.append(center_x)
                frame_numbers.append(frame_count)
            
            frame_count += 1
        
        cap.release()
        
        logger.info(f"Processed {len(face_centers)} sampled frames")
        
        # Smooth the face centers
        smoothed_centers = self._smooth_positions(face_centers)
        
        # Generate crop data for all frames (interpolate)
        crop_data = self._generate_crop_data(
            smoothed_centers,
            frame_numbers,
            total_frames,
            width,
            height,
            crop_width,
            crop_height
        )
        
        return {
            "video_metadata": {
                "width": width,
                "height": height,
                "fps": fps,
                "total_frames": total_frames,
                "duration": duration,
                "crop_width": crop_width,
                "crop_height": crop_height
            },
            "crop_data": crop_data,
            "smoothed_centers": smoothed_centers
        }
    
    def _detect_face_center(self, frame: np.ndarray, width: int, height: int) -> float:
        """
        Detect face in frame and return center X coordinate
        Prioritizes the most prominent face (likely the speaker)
        
        Args:
            frame: Video frame
            width: Frame width
            height: Frame height
            
        Returns:
            X coordinate of face center (or frame center if no face detected)
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        results = self.face_detection.process(rgb_frame)
        
        if results.detections:
            # Select the most prominent face (largest, most centered)
            best_face = self._select_speaking_face(results.detections, width, height)
            
            if best_face:
                bbox = best_face.location_data.relative_bounding_box
                
                # Calculate center X coordinate
                center_x = (bbox.xmin + bbox.width / 2) * width
                
                return center_x
        
        # No face detected, return center of frame
        return width / 2
    
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
    
    def _smooth_positions(self, positions: List[float], window_size: int = 15) -> List[float]:
        """
        Apply moving average smoothing to prevent jittery camera movement
        
        Args:
            positions: List of X coordinates
            window_size: Size of smoothing window (higher = smoother but more lag)
            
        Returns:
            Smoothed positions
        """
        if len(positions) < window_size:
            window_size = max(3, len(positions) // 2)
        
        # Apply moving average filter
        smoothed = np.convolve(
            positions,
            np.ones(window_size) / window_size,
            mode='same'
        )
        
        # Fix edges (convolve artifacts)
        for i in range(window_size // 2):
            smoothed[i] = np.mean(positions[:i+window_size//2+1])
            smoothed[-(i+1)] = np.mean(positions[-(i+window_size//2+1):])
        
        return smoothed.tolist()
    
    def _generate_crop_data(
        self,
        smoothed_centers: List[float],
        frame_numbers: List[int],
        total_frames: int,
        width: int,
        height: int,
        crop_width: int,
        crop_height: int
    ) -> List[Dict]:
        """
        Generate crop coordinates for all frames (with interpolation)
        
        Args:
            smoothed_centers: Smoothed face center X coordinates
            frame_numbers: Frame numbers that were sampled
            total_frames: Total frames in video
            width: Original video width
            height: Original video height
            crop_width: Target crop width
            crop_height: Target crop height
            
        Returns:
            List of crop data for each frame
        """
        crop_data = []
        
        # Interpolate for all frames
        all_centers = np.interp(
            range(total_frames),
            frame_numbers,
            smoothed_centers
        )
        
        for frame_num, center_x in enumerate(all_centers):
            # Calculate crop X position (center the crop on the face)
            crop_x = int(center_x - crop_width / 2)
            
            # Constrain to frame boundaries
            crop_x = max(0, min(crop_x, width - crop_width))
            
            # Y is always 0 (top of frame) since we're cropping full height
            crop_y = 0
            
            crop_data.append({
                "frame": frame_num,
                "x": crop_x,
                "y": crop_y,
                "width": crop_width,
                "height": crop_height,
                "center_x": float(center_x)
            })
        
        return crop_data
    
    def __del__(self):
        """Cleanup MediaPipe resources"""
        if hasattr(self, 'face_detection'):
            self.face_detection.close()


class KalmanSmoother:
    """
    Alternative smoothing using Kalman Filter
    More sophisticated than moving average, better for real-time tracking
    """
    
    def __init__(self, process_variance: float = 1e-5, measurement_variance: float = 1e-1):
        """
        Initialize Kalman Filter
        
        Args:
            process_variance: How much we trust the model
            measurement_variance: How much we trust the measurements
        """
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimate = None
        self.error = 1.0
    
    def update(self, measurement: float) -> float:
        """
        Update filter with new measurement
        
        Args:
            measurement: New position measurement
            
        Returns:
            Filtered position
        """
        if self.estimate is None:
            self.estimate = measurement
            return measurement
        
        # Prediction
        prediction = self.estimate
        prediction_error = self.error + self.process_variance
        
        # Update
        kalman_gain = prediction_error / (prediction_error + self.measurement_variance)
        self.estimate = prediction + kalman_gain * (measurement - prediction)
        self.error = (1 - kalman_gain) * prediction_error
        
        return self.estimate
    
    def smooth(self, positions: List[float]) -> List[float]:
        """
        Smooth entire sequence of positions
        
        Args:
            positions: List of positions
            
        Returns:
            Smoothed positions
        """
        smoothed = []
        for pos in positions:
            smoothed.append(self.update(pos))
        
        return smoothed
