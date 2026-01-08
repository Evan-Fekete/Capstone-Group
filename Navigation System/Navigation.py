# ---------------------------------------------------------
#   BASIC MOTOR CONTROL + SIMPLE OBSTACLE AVOIDANCE
#   Raspberry Pi – 4 DC Motors 
# ---------------------------------------------------------

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# -----------------------------
# MOTOR PINS (Adjust if needed)
# -----------------------------
# Left motor
LEFT_IN1 = 17
LEFT_IN2 = 27
LEFT_ENA = 22   # PWM PINS FOR  RAPSBERRY PI MOTOR DRIVER, in1/2 = +- direction decision

# Right motor
RIGHT_IN3 = 23
RIGHT_IN4 = 24
RIGHT_ENB = 25  # PWM

# Set pins as output
MOTOR_PINS = [LEFT_IN1, LEFT_IN2, LEFT_ENA, RIGHT_IN3, RIGHT_IN4, RIGHT_ENB]
for pin in MOTOR_PINS:
    GPIO.setup(pin, GPIO.OUT)

# Setup PWM
left_pwm = GPIO.PWM(LEFT_ENA, 1000)
right_pwm = GPIO.PWM(RIGHT_ENB, 1000)
left_pwm.start(60)
right_pwm.start(60) # PULSE WIDTH MODULATION IT CONTROLS SPEED so 60% speed

# -----------------------------
# ULTRASONIC SENSOR (HC-SR04)
# -----------------------------
TRIG = 5
ECHO = 6
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.01)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo pulse
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Convert to cm
    return round(distance, 2) # basically what this code does is that it sends a sound pulse, waits for it to bounce back, measures time and converts it to distance, 17150 is half the speed of sound in cm


# -----------------------------
# MOTOR MOVEMENT FUNCTIONS
# -----------------------------

def stop():
    GPIO.output(LEFT_IN1, False)
    GPIO.output(LEFT_IN2, False)
    GPIO.output(RIGHT_IN3, False)
    GPIO.output(RIGHT_IN4, False)
    print("STOP")

def run(t):
    # Forward
    GPIO.output(LEFT_IN1, True)
    GPIO.output(LEFT_IN2, False)
    GPIO.output(RIGHT_IN3, True)
    GPIO.output(RIGHT_IN4, False)
    print("FORWARD")
    time.sleep(t)
    stop()

def back(t):
    # Reverse
    GPIO.output(LEFT_IN1, False)
    GPIO.output(LEFT_IN2, True)
    GPIO.output(RIGHT_IN3, False)
    GPIO.output(RIGHT_IN4, True)
    print("BACKWARD")
    time.sleep(t)
    stop()

def spin_left(t):
    # Rotate left
    GPIO.output(LEFT_IN1, False)
    GPIO.output(LEFT_IN2, True)
    GPIO.output(RIGHT_IN3, True)
    GPIO.output(RIGHT_IN4, False)
    print("SPIN LEFT")
    time.sleep(t)
    stop()

def spin_right(t):
    # Rotate right
    GPIO.output(LEFT_IN1, True)
    GPIO.output(LEFT_IN2, False)
    GPIO.output(RIGHT_IN3, False)
    GPIO.output(RIGHT_IN4, True)
    print("SPIN RIGHT")
    time.sleep(t)
    stop()


# ---------------------------------------------------------
#         SIMPLE REACTIVE OBSTACLE AVOIDANCE LOOP
# ---------------------------------------------------------

try:
    print("Starting movement with obstacle avoidance...\n")

    while True:

        dist = get_distance()
        print(f"Distance: {dist} cm")

        if dist < 20:      # Obstacle detected
            print("Obstacle detected! Turning...")
            stop()
            time.sleep(0.3)
            spin_left(0.5)
        else:
            # Safe → move forward in small steps
            run(0.2)

except KeyboardInterrupt:
    print("\nStopping program...")

finally:
    stop()
    left_pwm.stop()
    right_pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")
#basically if object detected under 20 cm, then stop, rotate 0.5 seconds and resume loop (try to go forward again), if safe then move forward for 0.2 seconds then check again