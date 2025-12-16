# Piwars2026lib

A modular library system for robot control with motor drivers, joystick controllers, and GPIO management for Raspberry Pi.

## Features

- **Motor Control**: L298N dual motor driver control with PWM speed control
- **Joystick Controller**: Pygame-based joystick input handling with deadzone support
- **GPIO Management**: Centralized GPIO configuration and initialization
- **Drive Control**: Multiple drive algorithms (arcade, tank, curvature drive)

## Installation

```bash
pip install piwars2026lib
```

## Requirements

- Raspberry Pi (for GPIO functionality)
- Python 3.7+
- RPi.GPIO
- pygame

## Quick Start

```python
from piwars2026lib import MotorController, JoystickController, GPIOConfig, DriveControl
import pygame

# Initialize
pygame.init()
gpio = GPIOConfig()
gpio.setup()

# Setup motors with default pin configuration
pins = GPIOConfig.get_default_pins()
motors = MotorController(
    ena_pin=pins['ENA'],
    in1_pin=pins['IN1'],
    in2_pin=pins['IN2'],
    enb_pin=pins['ENB'],
    in3_pin=pins['IN3'],
    in4_pin=pins['IN4']
)

# Setup joystick
joystick = JoystickController(joystick_id=0, deadzone=0.1)

# Control loop
clock = pygame.time.Clock()
try:
    while True:
        joystick.pump_events()
        x, y = joystick.get_left_stick()
        left, right = DriveControl.arcade_drive(y, x)
        motors.set_tank_drive(left, right)
        clock.tick(50)
except KeyboardInterrupt:
    pass
finally:
    motors.cleanup()
    joystick.cleanup()
    gpio.cleanup()
    pygame.quit()
```

## API Documentation

### MotorController

Controls dual motors using L298N driver.

```python
motors = MotorController(ena_pin, in1_pin, in2_pin, enb_pin, in3_pin, in4_pin, pwm_freq=1000)
motors.set_motor_speed('A', speed)  # speed: -100 to 100
motors.set_tank_drive(left_speed, right_speed)
motors.stop_all()
motors.cleanup()
```

### JoystickController

Manages joystick input and provides normalized control values.

```python
joystick = JoystickController(joystick_id=0, deadzone=0.1)
x, y = joystick.get_left_stick()
x, y = joystick.get_right_stick()
value = joystick.get_axis(axis_id)
button = joystick.get_button(button_id)
joystick.pump_events()
joystick.cleanup()
```

### GPIOConfig

Manages GPIO configuration and initialization.

```python
gpio = GPIOConfig(mode=GPIO.BCM, warnings=False)
gpio.setup()
pins = GPIOConfig.get_default_pins()
gpio.cleanup()
```

### DriveControl

Provides various drive control algorithms.

```python
# Arcade drive
left, right = DriveControl.arcade_drive(y_axis, x_axis)

# Tank drive
left, right = DriveControl.tank_drive(left_y, right_y)

# Curvature drive
left, right = DriveControl.curvature_drive(y_axis, x_axis, quick_turn_threshold=0.1)
```

## Default Pin Configuration

The default pin configuration (BCM numbering) is:
- ENA: 13 (Motor A speed control - PWM)
- IN1: 19 (Motor A direction)
- IN2: 26 (Motor A direction)
- ENB: 12 (Motor B speed control - PWM)
- IN3: 16 (Motor B direction)
- IN4: 20 (Motor B direction)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

