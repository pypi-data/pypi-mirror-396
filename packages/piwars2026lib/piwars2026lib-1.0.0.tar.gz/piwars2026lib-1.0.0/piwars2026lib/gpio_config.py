"""
GPIO Configuration Library
Handles GPIO setup and configuration
"""
import RPi.GPIO as GPIO


class GPIOConfig:
    """Manages GPIO configuration and initialization"""
    
    # Default pin definitions (BCM numbering)
    DEFAULT_PINS = {
        'ENA': 13,  # Motor A speed control (PWM)
        'IN1': 19,  # Motor A direction
        'IN2': 26,  # Motor A direction
        'ENB': 12,  # Motor B speed control (PWM)
        'IN3': 16,  # Motor B direction
        'IN4': 20,  # Motor B direction
    }
    
    def __init__(self, mode=GPIO.BCM, warnings=False):
        """
        Initialize GPIO configuration
        
        Args:
            mode: GPIO mode (GPIO.BCM or GPIO.BOARD)
            warnings: Enable GPIO warnings (default: False)
        """
        self.mode = mode
        self.warnings = warnings
        self.initialized = False
    
    def setup(self):
        """Setup GPIO with configured settings"""
        GPIO.setmode(self.mode)
        GPIO.setwarnings(self.warnings)
        self.initialized = True
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.initialized:
            GPIO.cleanup()
            self.initialized = False
    
    @staticmethod
    def get_default_pins():
        """Get default pin configuration"""
        return GPIOConfig.DEFAULT_PINS.copy()

