"""
Motor Control Library
Handles L298N motor driver control for dual motors
"""
import RPi.GPIO as GPIO


class MotorController:
    """Controls dual motors using L298N driver"""
    
    def __init__(self, ena_pin, in1_pin, in2_pin, enb_pin, in3_pin, in4_pin, pwm_freq=1000):
        """
        Initialize motor controller
        
        Args:
            ena_pin: Motor A speed control (PWM) pin
            in1_pin: Motor A direction pin 1
            in2_pin: Motor A direction pin 2
            enb_pin: Motor B speed control (PWM) pin
            in3_pin: Motor B direction pin 1
            in4_pin: Motor B direction pin 2
            pwm_freq: PWM frequency in Hz (default: 1000)
        """
        self.ena = ena_pin
        self.in1 = in1_pin
        self.in2 = in2_pin
        self.enb = enb_pin
        self.in3 = in3_pin
        self.in4 = in4_pin
        
        # Setup GPIO pins
        GPIO.setup(self.ena, GPIO.OUT)
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.enb, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)
        GPIO.setup(self.in4, GPIO.OUT)
        
        # Create PWM instances
        self.pwm_a = GPIO.PWM(self.ena, pwm_freq)
        self.pwm_b = GPIO.PWM(self.enb, pwm_freq)
        self.pwm_a.start(0)
        self.pwm_b.start(0)
    
    def set_motor_speed(self, motor, speed):
        """
        Set motor speed and direction
        
        Args:
            motor: 'A' or 'B'
            speed: -100 to 100 (negative = reverse, positive = forward)
        """
        speed = max(-100, min(100, speed))  # Clamp to range
        
        if motor == 'A':
            pwm = self.pwm_a
            in1, in2 = self.in1, self.in2
        elif motor == 'B':
            pwm = self.pwm_b
            in1, in2 = self.in3, self.in4
        else:
            raise ValueError(f"Motor must be 'A' or 'B', got '{motor}'")
        
        if abs(speed) < 1:  # Stop
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            pwm.ChangeDutyCycle(0)
        elif speed > 0:  # Forward
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            pwm.ChangeDutyCycle(abs(speed))
        else:  # Reverse
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
            pwm.ChangeDutyCycle(abs(speed))
    
    def set_tank_drive(self, left_speed, right_speed):
        """
        Set both motors for tank drive
        
        Args:
            left_speed: Speed for left motor (-100 to 100)
            right_speed: Speed for right motor (-100 to 100)
        """
        self.set_motor_speed('A', left_speed)
        self.set_motor_speed('B', right_speed)
    
    def stop_all(self):
        """Stop all motors"""
        self.set_motor_speed('A', 0)
        self.set_motor_speed('B', 0)
    
    def cleanup(self):
        """Clean up PWM and GPIO resources"""
        self.stop_all()
        self.pwm_a.stop()
        self.pwm_b.stop()

