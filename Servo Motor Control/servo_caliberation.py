from gpiozero import AngularServo
from time import sleep

# --- SAFE CONFIGURATION ---
# We are shrinking the range to ensure we don't hit physical stops.
# Standard "Safe" Servo range is usually 1.0ms to 2.0ms
SERVO_PIN = 18

print("Initializing Servo with SAFE range (1000us - 2000us)...")

try:
    # Try a narrower pulse width first to avoid hitting mechanical stops
    servo = AngularServo(
        SERVO_PIN,
        min_angle=-45,   # Smaller angle range
        max_angle=45,
        min_pulse_width=0.001, # 1.0ms (Standard neutral-ish)
        max_pulse_width=0.002  # 2.0ms (Standard high-ish)
    )
except Exception as e:
    print(f"Error initializing: {e}")

def test_positions():
    print("--- STARTING TEST ---")
    
    print("1. Moving to CENTER (0 degrees)...")
    servo.angle = 0
    sleep(2)
    
    print("2. Moving to -45 degrees...")
    servo.angle = -45
    sleep(2)
    
    print("3. Moving to +45 degrees...")
    servo.angle = 45
    sleep(2)

    print("4. Wiggle test...")
    for _ in range(3):
        servo.angle = 10
        sleep(0.3)
        servo.angle = -10
        sleep(0.3)
        
    print("--- TEST COMPLETE ---")
    servo.angle = 0
    sleep(0.5)

if __name__ == "__main__":
    try:
        test_positions()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        servo.detach() # Crucial to stop the jitter
        print("Servo detached.")

