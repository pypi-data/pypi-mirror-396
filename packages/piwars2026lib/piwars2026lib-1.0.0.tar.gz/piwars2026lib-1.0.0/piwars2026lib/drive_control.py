"""
Drive Control Library
Provides high-level drive control algorithms (arcade drive, tank drive, etc.)
"""
import math


class DriveControl:
    """Provides various drive control algorithms"""
    
    @staticmethod
    def arcade_drive(y_axis, x_axis):
        """
        Arcade drive mixing: y_axis controls forward/backward, x_axis controls rotation
        
        Args:
            y_axis: Forward/backward input (-1.0 to 1.0)
            x_axis: Left/right rotation input (-1.0 to 1.0)
            
        Returns:
            Tuple of (left_speed, right_speed) in range -100 to 100
        """
        # Tank drive mixing (arcade drive)
        left_speed = (y_axis + x_axis) * 100
        right_speed = (y_axis - x_axis) * 100
        
        # Clamp values to -100 to 100
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        return left_speed, right_speed
    
    @staticmethod
    def tank_drive(left_y, right_y):
        """
        Tank drive: each stick controls one side
        
        Args:
            left_y: Left stick Y-axis (-1.0 to 1.0)
            right_y: Right stick Y-axis (-1.0 to 1.0)
            
        Returns:
            Tuple of (left_speed, right_speed) in range -100 to 100
        """
        left_speed = left_y * 100
        right_speed = right_y * 100
        
        # Clamp values to -100 to 100
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        return left_speed, right_speed
    
    @staticmethod
    def curvature_drive(y_axis, x_axis, quick_turn_threshold=0.1):
        """
        Curvature drive: similar to arcade but with quick turn capability
        
        Args:
            y_axis: Forward/backward input (-1.0 to 1.0)
            x_axis: Left/right rotation input (-1.0 to 1.0)
            quick_turn_threshold: Threshold for quick turn mode
            
        Returns:
            Tuple of (left_speed, right_speed) in range -100 to 100
        """
        if abs(y_axis) < quick_turn_threshold:
            # Quick turn mode
            left_speed = x_axis * 100
            right_speed = -x_axis * 100
        else:
            # Normal curvature drive
            left_speed = (y_axis + x_axis * abs(y_axis)) * 100
            right_speed = (y_axis - x_axis * abs(y_axis)) * 100
        
        # Clamp values to -100 to 100
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        return left_speed, right_speed

