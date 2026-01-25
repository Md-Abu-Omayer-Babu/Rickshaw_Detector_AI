import numpy as np
from typing import Tuple, Dict, List, Optional
from collections import defaultdict
from app.core.config import settings, logger


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class LineCrossingDetector:
    def __init__(
        self,
        line_start: Tuple[float, float],
        line_end: Tuple[float, float],
        frame_width: int,
        frame_height: int,
        use_percentage: bool = True
    ):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Convert percentage coordinates to pixels if needed
        if use_percentage:
            self.line_start = Point(
                line_start[0] * frame_width / 100,
                line_start[1] * frame_height / 100
            )
            self.line_end = Point(
                line_end[0] * frame_width / 100,
                line_end[1] * frame_height / 100
            )
        else:
            self.line_start = Point(line_start[0], line_start[1])
            self.line_end = Point(line_end[0], line_end[1])
        
        # Track object positions across frames
        self.object_positions: Dict[str, List[Point]] = defaultdict(list)
        self.entry_count = 0
        self.exit_count = 0
        self.crossed_objects = set()  # To avoid counting same object multiple times
        
        logger.info(f"LineCrossingDetector initialized: "
                   f"line from ({self.line_start.x:.1f}, {self.line_start.y:.1f}) "
                   f"to ({self.line_end.x:.1f}, {self.line_end.y:.1f})")
    
    def get_line_pixels(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return (
            (int(self.line_start.x), int(self.line_start.y)),
            (int(self.line_end.x), int(self.line_end.y))
        )
    
    def _get_object_center(self, bbox: np.ndarray) -> Point:
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return Point(center_x, center_y)
    
    def _ccw(self, A: Point, B: Point, C: Point) -> float:
        return (C.y - A.y) * (B.x - A.x) - (B.y - A.y) * (C.x - A.x)
    
    def _intersects(self, A: Point, B: Point, C: Point, D: Point) -> bool:
        return (self._ccw(A, C, D) != self._ccw(B, C, D) and
                self._ccw(A, B, C) != self._ccw(A, B, D))
    
    def _get_side_of_line(self, point: Point) -> int:
        value = ((self.line_end.x - self.line_start.x) * (point.y - self.line_start.y) -
                 (self.line_end.y - self.line_start.y) * (point.x - self.line_start.x))
        
        if value > settings.crossing_threshold:
            return 1
        elif value < -settings.crossing_threshold:
            return -1
        else:
            return 0
    
    def update(
        self,
        object_id: str,
        bbox: np.ndarray,
        frame_number: int
    ) -> Optional[str]:
        # Get object center
        current_center = self._get_object_center(bbox)
        
        # Get previous position
        if object_id in self.object_positions and len(self.object_positions[object_id]) > 0:
            previous_center = self.object_positions[object_id][-1]
            
            # Check if object crossed the line
            if self._intersects(previous_center, current_center, 
                              self.line_start, self.line_end):
                
                # Determine direction based on which side of the line
                prev_side = self._get_side_of_line(previous_center)
                curr_side = self._get_side_of_line(current_center)
                
                # Only count if object hasn't been counted recently
                if object_id not in self.crossed_objects:
                    if prev_side < curr_side:
                        # Crossed from bottom to top (or left to right) - Entry
                        self.entry_count += 1
                        self.crossed_objects.add(object_id)
                        logger.info(f"Entry detected: object {object_id} at frame {frame_number}")
                        
                        # Keep history manageable - limit to recent frames
                        self.object_positions[object_id].append(current_center)
                        if len(self.object_positions[object_id]) > settings.track_history_length:
                            self.object_positions[object_id].pop(0)
                        
                        return "entry"
                    
                    elif prev_side > curr_side:
                        # Crossed from top to bottom (or right to left) - Exit
                        self.exit_count += 1
                        self.crossed_objects.add(object_id)
                        logger.info(f"Exit detected: object {object_id} at frame {frame_number}")
                        
                        # Keep history manageable
                        self.object_positions[object_id].append(current_center)
                        if len(self.object_positions[object_id]) > settings.track_history_length:
                            self.object_positions[object_id].pop(0)
                        
                        return "exit"
        
        # Update position history
        self.object_positions[object_id].append(current_center)
        
        # Keep history manageable - limit to recent positions
        if len(self.object_positions[object_id]) > settings.track_history_length:
            self.object_positions[object_id].pop(0)
        
        return None
    
    def reset_crossed_objects(self):
        self.crossed_objects.clear()
    
    def get_counts(self) -> Tuple[int, int, int]:
        return self.entry_count, self.exit_count, self.entry_count - self.exit_count
    
    def reset_counts(self):
        self.entry_count = 0
        self.exit_count = 0
        self.crossed_objects.clear()
        self.object_positions.clear()
        logger.info("Line crossing counts reset")


class SimpleTracker:
    def __init__(self, iou_threshold: float = 0.3, max_frames_to_skip: int = 10):
        self.iou_threshold = iou_threshold
        self.max_frames_to_skip = max_frames_to_skip
        self.next_id = 0
        self.tracks: Dict[int, Dict] = {}  # track_id -> {bbox, frames_skipped}
    
    def _calculate_iou(self, box1: np.ndarray, box2: np.ndarray) -> float:
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Calculate intersection area
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union area
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def update(self, detections: np.ndarray) -> Dict[int, np.ndarray]:
        # Mark all tracks as not updated
        for track_id in self.tracks:
            self.tracks[track_id]['frames_skipped'] += 1
        
        # Match detections to existing tracks
        matched_tracks = {}
        unmatched_detections = []
        
        for detection in detections:
            best_iou = 0
            best_track_id = None
            
            # Find best matching track
            for track_id, track_info in self.tracks.items():
                iou = self._calculate_iou(detection, track_info['bbox'])
                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id
            
            if best_track_id is not None:
                # Update existing track
                self.tracks[best_track_id]['bbox'] = detection
                self.tracks[best_track_id]['frames_skipped'] = 0
                matched_tracks[best_track_id] = detection
            else:
                # New detection
                unmatched_detections.append(detection)
        
        # Create new tracks for unmatched detections
        for detection in unmatched_detections:
            track_id = self.next_id
            self.next_id += 1
            self.tracks[track_id] = {
                'bbox': detection,
                'frames_skipped': 0
            }
            matched_tracks[track_id] = detection
        
        # Remove tracks that have been missing for too long
        tracks_to_remove = [
            track_id for track_id, track_info in self.tracks.items()
            if track_info['frames_skipped'] > self.max_frames_to_skip
        ]
        
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
        
        return matched_tracks
