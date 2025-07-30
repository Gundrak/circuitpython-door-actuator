# SPDX-License-Identifier: MIT

import time
import board
import neopixel
import random
from digitalio import DigitalInOut, Direction, Pull

# Hardware pin setup
lock_output = DigitalInOut(board.SDA)
lock_output.direction = Direction.OUTPUT  # in3 on L298N
lock_output.value = False

# L298N motor driver control pins
motor_up = DigitalInOut(board.SCL)        # Controls upward movement when HIGH
motor_down = DigitalInOut(board.D21)      # Controls downward movement when HIGH
motor_up.direction = Direction.OUTPUT     # in1 on L298N
motor_down.direction = Direction.OUTPUT   # in2 on L298N

# NeoPixel setup
number_of_pixels = 12 # The number of LEDs on the strip
led_strip = neopixel.NeoPixel(board.A0, number_of_pixels, bpp=3, brightness=0.1, pixel_order=neopixel.GRB)

# Color definitions
WHITE = (200, 200, 200)
OFF = (0, 0, 0)

# Switch setup
main_switch = DigitalInOut(board.D5)
main_switch.direction = Direction.INPUT
main_switch.pull = Pull.UP

# Secret switches for unlock sequence
secret_switch_1 = DigitalInOut(board.A1)
secret_switch_1.direction = Direction.INPUT
secret_switch_1.pull = Pull.UP

secret_switch_2 = DigitalInOut(board.MISO)
secret_switch_2.direction = Direction.INPUT
secret_switch_2.pull = Pull.UP

# Initialize hardware to safe state
motor_up.value = False
motor_down.value = False
led_strip.fill(OFF)
led_strip.show()

# Configuration constants
MOVEMENT_DURATION = 13  # Actuator movement duration in seconds
BRIGHTNESS_UPDATE_INTERVAL = 0.1  # How often to update brightness (smoother dimming)
SPARKLE_UPDATE_INTERVAL = 2  # How often to update sparkle pattern (seconds)
SPARKLE_PROBABILITY = 0.8  # Probability that a pixel is on during sparkle effect
MIN_BRIGHTNESS = 0.1
MAX_BRIGHTNESS = 0.9
LOCK_OPEN_DURATION = 0.5  # How long to keep lock open in seconds
SECRET_SEQUENCE_TIMEOUT = 15  # Max time to complete secret sequence
TARGET_SEQUENCE = ["secret_switch_1", "secret_switch_2", "secret_switch_2", "secret_switch_1"]

# State tracking
prev_main_switch = main_switch.value
prev_secret_switch_1 = secret_switch_1.value
prev_secret_switch_2 = secret_switch_2.value

actuator_state = 'stopped'  # 'stopped', 'moving_up', 'moving_down'
next_movement_direction = 'up'  # Direction for next movement from stopped state
last_known_position = 'bottom'  # 'top' or 'bottom'

# Movement control
is_moving = False
movement_start_time = 0
current_direction = None

# Secret unlock system
secret_presses = []
lock_is_open = False
lock_opened_time = 0

# Animation timing
last_brightness_update = 0
last_sparkle_update = 0

def update_led_animation():
    """Update NeoPixel animation based on actuator state"""
    global last_known_position, movement_start_time, last_sparkle_update
    
    current_time = time.monotonic()
    brightness_changed = False

    if actuator_state == 'moving_up':
        # Fade brightness up as actuator moves up
        elapsed = min(time.monotonic() - movement_start_time, MOVEMENT_DURATION)
        brightness = MIN_BRIGHTNESS + (MAX_BRIGHTNESS - MIN_BRIGHTNESS) * (elapsed / MOVEMENT_DURATION)
        led_strip.brightness = brightness
        brightness_changed = True
        
    elif actuator_state == 'moving_down':
        # Fade brightness down as actuator moves down
        elapsed = min(time.monotonic() - movement_start_time, MOVEMENT_DURATION)
        brightness = MAX_BRIGHTNESS - (MAX_BRIGHTNESS - MIN_BRIGHTNESS) * (elapsed / MOVEMENT_DURATION)
        led_strip.brightness = brightness
        brightness_changed = True
        
    elif actuator_state == "stopped" and last_known_position == "top":
        # Stay bright when stopped at top
        if led_strip.brightness != MAX_BRIGHTNESS:
          led_strip.brightness = MAX_BRIGHTNESS
          brightness_changed = True
    else:
        # Off when stopped at bottom
      if led_strip.brightness != MIN_BRIGHTNESS:
        led_strip.brightness = MIN_BRIGHTNESS
        brightness_changed = True
    
    # Update sparkle pattern at its own interval
    if current_time - last_sparkle_update >= SPARKLE_UPDATE_INTERVAL:
      if actuator_state != "stopped" or last_known_position == "top":
        apply_sparkle_effect()
      else:
        led_strip.fill(OFF)
      last_sparkle_update = current_time
      led_strip.show()
    elif brightness_changed:
      # Only update display if brightness changed (keeps existing pattern)
      led_strip.show()

def apply_sparkle_effect():
    """Apply random sparkle effect to LED strip"""
    for i in range(len(led_strip)):
        if random.random() < SPARKLE_PROBABILITY:
            led_strip[i] = WHITE
        else:
            led_strip[i] = OFF

def start_movement(direction):
    """Start actuator movement in specified direction"""
    global is_moving, movement_start_time, current_direction, actuator_state

    if direction == 'up':
        motor_up.value = True
        motor_down.value = False
        actuator_state = 'moving_up'
        print("Starting actuator UP movement")
    else:  # direction == 'down'
        motor_up.value = False
        motor_down.value = True
        actuator_state = 'moving_down'
        print("Starting actuator DOWN movement")

    is_moving = True
    movement_start_time = time.monotonic()
    current_direction = direction

def stop_movement():
    """Stop actuator movement and update position tracking"""
    global is_moving, current_direction, actuator_state, last_known_position

    # Update position based on last movement direction
    if current_direction == 'up':
        last_known_position = 'top'
    elif current_direction == 'down':
        last_known_position = 'bottom'

    # Turn off motors
    motor_up.value = False
    motor_down.value = False
    
    # Reset movement state
    is_moving = False
    current_direction = None
    actuator_state = 'stopped'
    print("Actuator movement stopped")

def unlock_door():
    """Activate the door lock for configured duration"""
    global lock_is_open, lock_opened_time
    lock_is_open = True
    lock_opened_time = time.monotonic()
    print("Secret door unlocked")

def check_secret_sequence():
    """Check if the secret switch sequence has been entered correctly"""
    global secret_presses
    
    current_time = time.monotonic()
    
    # Detect new presses (transition from released to pressed)
    if prev_secret_switch_1 and not secret_switch_1.value:
        secret_presses.append({
            "timestamp": current_time,
            "switch": "secret_switch_1"
        })

    if prev_secret_switch_2 and not secret_switch_2.value:
        secret_presses.append({
            "timestamp": current_time,
            "switch": "secret_switch_2"
        })
    
    # Remove old presses that are outside the sequence timeout
    cutoff_time = current_time - SECRET_SEQUENCE_TIMEOUT - 5
    secret_presses = [press for press in secret_presses if press["timestamp"] > cutoff_time]

    # Check if we have enough presses to form the target sequence
    if len(secret_presses) >= len(TARGET_SEQUENCE):
        # Look for the target sequence in recent presses
        for i in range(len(secret_presses) - len(TARGET_SEQUENCE) + 1):
            candidate_presses = secret_presses[i:i + len(TARGET_SEQUENCE)]
            candidate_sequence = [press["switch"] for press in candidate_presses]

            if candidate_sequence == TARGET_SEQUENCE:
                # Check if sequence was completed within time limit
                sequence_duration = candidate_presses[-1]["timestamp"] - candidate_presses[0]["timestamp"]
                
                if sequence_duration <= SECRET_SEQUENCE_TIMEOUT:
                    secret_presses.clear()  # Prevent repeated unlocks
                    unlock_door()
                    return

def handle_main_switch_press():
    """Handle main switch press based on current actuator state"""
    global next_movement_direction
    
    if actuator_state == 'stopped':
        # Start movement in planned direction
        start_movement(next_movement_direction)
    elif actuator_state == 'moving_up':
        # Emergency stop - next press will move down
        stop_movement()
        next_movement_direction = 'down'
        print("Emergency stop during UP movement - next press will move DOWN")
    elif actuator_state == 'moving_down':
        # Emergency stop - next press will move up
        stop_movement()
        next_movement_direction = 'up'
        print("Emergency stop during DOWN movement - next press will move UP")

def check_movement_completion():
    """Check if movement duration has elapsed and handle completion"""
    global next_movement_direction
    
    if is_moving and (time.monotonic() - movement_start_time >= MOVEMENT_DURATION):
        # Movement completed naturally - set next direction
        if actuator_state == 'moving_up':
            next_movement_direction = 'down'
            print("UP movement completed - next press will move DOWN")
        elif actuator_state == 'moving_down':
            next_movement_direction = 'up'
            print("DOWN movement completed - next press will move UP")

        stop_movement()

def update_lock_state():
    """Update lock output based on unlock state"""
    global lock_is_open
    
    # Close lock after configured duration
    if lock_is_open and (time.monotonic() - lock_opened_time >= LOCK_OPEN_DURATION):
        lock_is_open = False
    
    lock_output.value = lock_is_open

# Main control loop
while True:
    current_time = time.monotonic()
    
    # Read current switch states
    current_main_switch = main_switch.value
    current_secret_1 = secret_switch_1.value
    current_secret_2 = secret_switch_2.value

    # Check secret unlock sequence
    check_secret_sequence()
    
    # Update lock state
    update_lock_state()
        
    # Handle main switch press (falling edge detection)
    if prev_main_switch and not current_main_switch:
        handle_main_switch_press()

    # Check for movement completion
    check_movement_completion()

    # Update LED brightness at regular intervals for smooth dimming
    if current_time - last_brightness_update >= BRIGHTNESS_UPDATE_INTERVAL:
        update_led_animation()
        last_brightness_update = current_time

    # Store previous switch states for edge detection
    prev_main_switch = current_main_switch
    prev_secret_switch_1 = current_secret_1
    prev_secret_switch_2 = current_secret_2

    # Small delay for switch debouncing and system responsiveness
    time.sleep(0.01)