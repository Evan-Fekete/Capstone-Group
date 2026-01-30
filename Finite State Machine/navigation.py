# navigation.py
# MECANUM WHEEL MOTOR CONTROL + REACTIVE OBSTACLE AVOIDANCE
# Raspberry Pi 5 — using gpiozero

from gpiozero import DigitalOutputDevice, PWMOutputDevice, DistanceSensor
from time import sleep
import random

# -----------------------------
# CONFIGURATION
# -----------------------------
DEBUG = True

DEFAULT_SPEED = 0.50        # 50% — good balance of control & power
SLOW_SPEED = 0.35           # used during avoidance
OBSTACLE_THRESHOLD = 25.0   # cm

def debug_print(message):
    if DEBUG:
        print(f"[NAV] {message}")

# -----------------------------
# MOTOR PINS (your current wiring)
# -----------------------------
# Left back motor
LEFT_BACK_IN1 = 27
LEFT_BACK_IN2 = 17
LEFT_BACK_ENB = 18

# Left front motor
LEFT_FRONT_IN1 = 22
LEFT_FRONT_IN2 = 20
LEFT_FRONT_ENA = 12

# Right front motor
RIGHT_FRONT_IN1 = 21
RIGHT_FRONT_IN2 = 13
RIGHT_FRONT_ENA = 16

# Right back motor
RIGHT_BACK_IN1 = 26
RIGHT_BACK_IN2 = 19
RIGHT_BACK_ENB = 25

# Direction pins
left_back_in1   = DigitalOutputDevice(LEFT_BACK_IN1)
left_back_in2   = DigitalOutputDevice(LEFT_BACK_IN2)
left_front_in1  = DigitalOutputDevice(LEFT_FRONT_IN1)
left_front_in2  = DigitalOutputDevice(LEFT_FRONT_IN2)
right_front_in1 = DigitalOutputDevice(RIGHT_FRONT_IN1)
right_front_in2 = DigitalOutputDevice(RIGHT_FRONT_IN2)
right_back_in1  = DigitalOutputDevice(RIGHT_BACK_IN1)
right_back_in2  = DigitalOutputDevice(RIGHT_BACK_IN2)

# PWM (start at 0)
left_front_pwm  = PWMOutputDevice(LEFT_FRONT_ENA,  frequency=1000, initial_value=0)
left_back_pwm   = PWMOutputDevice(LEFT_BACK_ENB,   frequency=1000, initial_value=0)
right_front_pwm = PWMOutputDevice(RIGHT_FRONT_ENA, frequency=1000, initial_value=0)
right_back_pwm  = PWMOutputDevice(RIGHT_BACK_ENB,  frequency=1000, initial_value=0)

# Ultrasonic sensor
sensor = DistanceSensor(echo=24, trigger=23, max_distance=4)

# -----------------------------
# LOW-LEVEL HELPERS
# -----------------------------
def set_all_speed(speed):
    """Set same speed for all four motors (0.0 to 1.0)"""
    left_front_pwm.value  = speed
    left_back_pwm.value   = speed
    right_front_pwm.value = speed
    right_back_pwm.value  = speed

def set_individual_speeds(lf, lb, rf, rb):
    left_front_pwm.value  = lf
    left_back_pwm.value   = lb
    right_front_pwm.value = rf
    right_back_pwm.value  = rb

def stop():
    """Stop all motors"""
    left_front_in1.off();  left_front_in2.off()
    left_back_in1.off();   left_back_in2.off()
    right_front_in1.off(); right_front_in2.off()
    right_back_in1.off();  right_back_in2.off()
    set_all_speed(0)
    debug_print("Stopped")

# -----------------------------
# DIRECTION HELPERS
# -----------------------------
def all_forward():
    left_front_in1.on();  left_front_in2.off()
    left_back_in1.on();   left_back_in2.off()
    right_front_in1.on(); right_front_in2.off()
    right_back_in1.on();  right_back_in2.off()

def all_backward():
    left_front_in1.off();  left_front_in2.on()
    left_back_in1.off();   left_back_in2.on()
    right_front_in1.off(); right_front_in2.on()
    right_back_in1.off();  right_back_in2.on()

# -----------------------------
# MOVEMENT PRIMITIVES
# -----------------------------
def forward(t, speed=DEFAULT_SPEED):
    set_all_speed(speed)
    all_forward()
    debug_print(f"Forward {t}s @ {speed:.2f}")
    sleep(t)
    stop()

def backward(t, speed=DEFAULT_SPEED):
    set_all_speed(speed)
    all_backward()
    debug_print(f"Backward {t}s @ {speed:.2f}")
    sleep(t)
    stop()

def strafe_left(t, speed=DEFAULT_SPEED):
    set_all_speed(speed)
    left_front_in1.off();  left_front_in2.on()   # LF back
    left_back_in1.on();    left_back_in2.off()   # LB forward
    right_front_in1.on();  right_front_in2.off() # RF forward
    right_back_in1.off();  right_back_in2.on()   # RB back
    debug_print(f"Strafe left {t}s @ {speed:.2f}")
    sleep(t)
    stop()

def strafe_right(t, speed=DEFAULT_SPEED):
    set_all_speed(speed)
    left_front_in1.on();   left_front_in2.off()  # LF forward
    left_back_in1.off();   left_back_in2.on()    # LB back
    right_front_in1.off(); right_front_in2.on()  # RF back
    right_back_in1.on();   right_back_in2.off()  # RB forward
    debug_print(f"Strafe right {t}s @ {speed:.2f}")
    sleep(t)
    stop()

def rotate_left(t, speed=DEFAULT_SPEED):   # CCW
    set_all_speed(speed)
    left_front_in1.off();  left_front_in2.on()   # left backward
    left_back_in1.off();   left_back_in2.on()
    right_front_in1.on();  right_front_in2.off() # right forward
    right_back_in1.on();   right_back_in2.off()
    debug_print(f"Rotate left (CCW) {t}s @ {speed:.2f}")
    sleep(t)
    stop()

def rotate_right(t, speed=DEFAULT_SPEED):  # CW
    set_all_speed(speed)
    left_front_in1.on();   left_front_in2.off()  # left forward
    left_back_in1.on();    left_back_in2.off()
    right_front_in1.off(); right_front_in2.on()  # right backward
    right_back_in1.off();  right_back_in2.on()
    debug_print(f"Rotate right (CW) {t}s @ {speed:.2f}")
    sleep(t)
    stop()

# -----------------------------
# SENSOR
# -----------------------------
def get_distance():
    try:
        dist = sensor.distance * 100
        if dist is None:
            return 400.0
        return round(dist, 2)
    except:
        return 400.0

# -----------------------------
# AVOIDANCE LOGIC
# -----------------------------
def avoid_obstacle():
    stop()
    sleep(0.2)

    # Small backup
    backward(0.3, SLOW_SPEED)

    # Choose strafe direction randomly (50/50)
    if random.random() < 0.5:
        strafe_left(0.7, SLOW_SPEED)
    else:
        strafe_right(0.7, SLOW_SPEED)

    # Small corrective rotation
    if random.random() < 0.5:
        rotate_left(0.35, SLOW_SPEED)
    else:
        rotate_right(0.35, SLOW_SPEED)

# -----------------------------
# MAIN REACTIVE STEP (call this frequently from FSM)
# -----------------------------
def reactive_step():
    dist = get_distance()
    debug_print(f"Distance: {dist:.1f} cm")

    if dist < OBSTACLE_THRESHOLD:
        debug_print("→ OBSTACLE DETECTED")
        avoid_obstacle()
    else:
        forward(0.18, DEFAULT_SPEED)

# -----------------------------
# CLEANUP
# -----------------------------
def cleanup():
    stop()
    left_front_pwm.close()
    left_back_pwm.close()
    right_front_pwm.close()
    right_back_pwm.close()
    left_back_in1.close()
    left_back_in2.close()
    left_front_in1.close()
    left_front_in2.close()
    right_front_in1.close()
    right_front_in2.close()
    right_back_in1.close()
    right_back_in2.close()
    sensor.close()
    debug_print("Navigation cleanup complete")

# -----------------------------
# Optional standalone test loop
# -----------------------------
if __name__ == "__main__":
    try:
        debug_print("Starting standalone reactive navigation test...")
        set_all_speed(DEFAULT_SPEED)
        while True:
            reactive_step()
            sleep(0.02)  # small loop delay
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        cleanup()


