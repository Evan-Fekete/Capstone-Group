from gpiozero import AngularServo
from time import sleep
import sys

# --- CONFIGURATION ---
SERVO_PIN = 18

# WE KNOW THIS WORKS: Using the "Safe Range" from your successful calibration.
# Range: -45 to +45 degrees
# Pulse: 1.0ms to 2.0ms
servo = AngularServo(
    SERVO_PIN,
    min_angle=-45,
    max_angle=45,
    min_pulse_width=0.001,
    max_pulse_width=0.002
)

# Global Variables
current_angle = 0
step_delay = 0.03  # Default speed
step_size = 5      # Degrees per step

def change_speed(level):
    """Sets the delay between movement steps."""
    global step_delay
    if level == '1':
        step_delay = 0.08  # Slow
        print(">> Speed set to SLOW")
    elif level == '2':
        step_delay = 0.03  # Medium
        print(">> Speed set to MEDIUM")
    elif level == '3':
        step_delay = 0.002 # Fast
        print(">> Speed set to FAST")

def move_servo_smoothly(target):
    """Moves the servo incrementally."""
    global current_angle
    
    # SAFETY: Clamp values to the safe limits
    if target > 45: 
        print(f"Limit Reached! Clamping to 45°.")
        target = 45
    if target < -45: 
        print(f"Limit Reached! Clamping to -45°.")
        target = -45
    
    print(f"Moving to {target}°...")

    # Determine direction
    if current_angle < target:
        step_dir = 1
    else:
        step_dir = -1

    # Move in steps
    start = int(current_angle)
    end = int(target)
    
    if start == end:
        return

    for angle in range(start, end, step_dir):
        servo.angle = angle
        sleep(step_delay)
    
    # Finalize position
    servo.angle = target
    current_angle = target

def print_menu():
    print("\n--- PI 5 SERVO CONTROL (Safe Mode) ---")
    print(" [a] Move Left")
    print(" [d] Move Right")
    print(" [0] Center Servo (0°)")
    print(" [1] Slow | [2] Medium | [3] Fast")
    print(" [q] Quit")
    print("--------------------------------------")

# --- MAIN LOOP ---
try:
    print("Initializing...")
    servo.angle = 0
    print("Servo centered.")
    
    while True:
        print_menu()
        cmd = input(f"Current: {current_angle}° | Command: ").lower().strip()
        
        if cmd == 'q':
            break
            
        elif cmd == 'a':
            new_target = current_angle - step_size
            move_servo_smoothly(new_target)
            
        elif cmd == 'd':
            new_target = current_angle + step_size
            move_servo_smoothly(new_target)
            
        elif cmd == '0':
            move_servo_smoothly(0)
            
        elif cmd in ['1', '2', '3']:
            change_speed(cmd)
            
        else:
            try:
                custom_angle = int(cmd)
                move_servo_smoothly(custom_angle)
            except ValueError:
                print("Invalid command.")

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    servo.detach()
    print("Servo detached.")


