"""
Joystick Controller Library
Handles joystick input and provides control interface
"""
import pygame


class JoystickController:
    """Manages joystick input and provides normalized control values"""
    
    def __init__(self, joystick_id=0, deadzone=0.1):
        """
        Initialize joystick controller
        
        Args:
            joystick_id: Joystick device ID (default: 0)
            deadzone: Deadzone threshold to prevent drift (default: 0.1)
        """
        self.deadzone = deadzone
        self.joystick_id = joystick_id
        self.joystick = None
        self.initialized = False
        
        # Initialize pygame joystick subsystem
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No joystick detected!")
        
        self.joystick = pygame.joystick.Joystick(joystick_id)
        self.joystick.init()
        self.initialized = True
        print(f"Connected to: {self.joystick.get_name()}")
    
    def get_axis(self, axis_id):
        """
        Get joystick axis value with deadzone applied
        
        Args:
            axis_id: Axis ID (0=X, 1=Y, etc.)
            
        Returns:
            Normalized axis value (-1.0 to 1.0)
        """
        if not self.initialized:
            return 0.0
        
        value = self.joystick.get_axis(axis_id)
        
        # Apply deadzone
        if abs(value) < self.deadzone:
            return 0.0
        
        return value
    
    def get_left_stick(self):
        """
        Get left stick values (X, Y)
        
        Returns:
            Tuple of (x, y) values (-1.0 to 1.0)
        """
        x = self.get_axis(0)  # Left/Right
        y = -self.get_axis(1)  # Forward/Back (inverted so up is positive)
        return x, y
    
    def get_right_stick(self):
        """
        Get right stick values (X, Y)
        
        Returns:
            Tuple of (x, y) values (-1.0 to 1.0)
        """
        x = self.get_axis(2)  # Left/Right
        y = -self.get_axis(3)  # Forward/Back (inverted so up is positive)
        return x, y
    
    def get_button(self, button_id):
        """
        Get button state
        
        Args:
            button_id: Button ID
            
        Returns:
            True if pressed, False otherwise
        """
        if not self.initialized:
            return False
        return self.joystick.get_button(button_id)
    
    def pump_events(self):
        """Pump pygame events (call this in main loop)"""
        pygame.event.pump()
    
    def cleanup(self):
        """Clean up joystick resources"""
        if self.joystick and self.initialized:
            self.joystick.quit()
        pygame.joystick.quit()

