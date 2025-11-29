import numpy as np
import math

def map_coordinates(x, y, src_w, src_h, dst_w, dst_h):
    """
    Maps coordinates from source resolution (webcam) to destination resolution (screen).
    Includes a margin to allow reaching edges easily.
    """
    # Define a margin to make it easier to reach the edges of the screen
    margin = 100  # pixels
    
    # Clamp x and y to the effective area
    x_clamped = np.clip(x * src_w, margin, src_w - margin)
    y_clamped = np.clip(y * src_h, margin, src_h - margin)
    
    # Normalize back to 0-1 range within the margin
    x_norm = (x_clamped - margin) / (src_w - 2 * margin)
    y_norm = (y_clamped - margin) / (src_h - 2 * margin)
    
    # Map to destination
    screen_x = np.interp(x_norm, [0, 1], [0, dst_w])
    screen_y = np.interp(y_norm, [0, 1], [0, dst_h])
    
    return int(screen_x), int(screen_y)

def calculate_distance(p1, p2):
    """
    Calculates Euclidean distance between two MediaPipe landmarks.
    """
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def smooth_coordinates(current_x, current_y, prev_x, prev_y, smoothing_factor=0.5):
    """
    Applies exponential smoothing to coordinates.
    smoothing_factor: 0.0 to 1.0. Higher value = less smoothing (more responsive), lower = more smoothing (less jitter).
    """
    new_x = prev_x + (current_x - prev_x) * smoothing_factor
    new_y = prev_y + (current_y - prev_y) * smoothing_factor
    return int(new_x), int(new_y)
