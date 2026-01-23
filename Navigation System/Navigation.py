# ---------------------------------------------------------
#   MECANUM WHEEL MOTOR CONTROL + OBSTACLE AVOIDANCE
#   Raspberry Pi 5 — 4 DC Motors (using gpiozero)
# ---------------------------------------------------------
from gpiozero import DigitalOutputDevice, PWMOutputDevice, DistanceSensor
from time import sleep

# -----------------------------
# DEBUG FLAG - Set to False to disable verbose output
# -----------------------------
DEBUG = True

def debug_print(message):
    """Print message only if DEBUG is enabled"""
    if DEBUG:
        print(message)

# -----------------------------
# MOTOR PINS
# NOTE: Avoiding GPIO 0-8 to prevent motors turning on at boot
# -----------------------------
# Left back motor
LEFT_BACK_IN1 = 27
LEFT_BACK_IN2 = 17

# Left front motor
LEFT_FRONT_IN1 = 22
LEFT_FRONT_IN2 = 20

# Right front motor
RIGHT_FRONT_IN1 = 21
RIGHT_FRONT_IN2 = 13

# Right back motor
RIGHT_BACK_IN1 = 26
RIGHT_BACK_IN2 = 19

# PWM enable pins (one per motor for individual speed control)
LEFT_FRONT_ENA = 12
LEFT_BACK_ENB = 18
RIGHT_FRONT_ENA = 16
RIGHT_BACK_ENB = 25

# Setup motor direction pins
left_back_in1 = DigitalOutputDevice(LEFT_BACK_IN1)
left_back_in2 = DigitalOutputDevice(LEFT_BACK_IN2)
left_front_in1 = DigitalOutputDevice(LEFT_FRONT_IN1)
left_front_in2 = DigitalOutputDevice(LEFT_FRONT_IN2)
right_front_in1 = DigitalOutputDevice(RIGHT_FRONT_IN1)
right_front_in2 = DigitalOutputDevice(RIGHT_FRONT_IN2)
right_back_in1 = DigitalOutputDevice(RIGHT_BACK_IN1)
right_back_in2 = DigitalOutputDevice(RIGHT_BACK_IN2)

# Setup PWM for individual motor speed control (0.0 to 1.0)
left_front_pwm = PWMOutputDevice(LEFT_FRONT_ENA, frequency=1000, initial_value=0.33)
left_back_pwm = PWMOutputDevice(LEFT_BACK_ENB, frequency=1000, initial_value=0.33)
right_front_pwm = PWMOutputDevice(RIGHT_FRONT_ENA, frequency=1000, initial_value=0.33)
right_back_pwm = PWMOutputDevice(RIGHT_BACK_ENB, frequency=1000, initial_value=0.33)

# -----------------------------
# ULTRASONIC SENSOR (HC-SR04)
# -----------------------------
TRIG = 23
ECHO = 24

sensor = DistanceSensor(echo=ECHO, trigger=TRIG, max_distance=4)

def get_distance():
    """Get distance in centimeters"""
    distance = sensor.distance * 100
    return round(distance, 2)

# -----------------------------
# SPEED CONTROL
# -----------------------------
def set_all_speed(speed):
    """Set speed for all motors (0.0 to 1.0)"""
    left_front_pwm.value = speed
    left_back_pwm.value = speed
    right_front_pwm.value = speed
    right_back_pwm.value = speed
    debug_print(f"All motors speed set to {int(speed * 100)}%")

def set_left_front_speed(speed):
    """Set speed for left front motor (0.0 to 1.0)"""
    left_front_pwm.value = speed

def set_left_back_speed(speed):
    """Set speed for left back motor (0.0 to 1.0)"""
    left_back_pwm.value = speed

def set_right_front_speed(speed):
    """Set speed for right front motor (0.0 to 1.0)"""
    right_front_pwm.value = speed

def set_right_back_speed(speed):
    """Set speed for right back motor (0.0 to 1.0)"""
    right_back_pwm.value = speed

def set_left_speed(speed):
    """Set speed for both left motors (0.0 to 1.0)"""
    left_front_pwm.value = speed
    left_back_pwm.value = speed

def set_right_speed(speed):
    """Set speed for both right motors (0.0 to 1.0)"""
    right_front_pwm.value = speed
    right_back_pwm.value = speed

def set_individual_speeds(lf, lb, rf, rb):
    """Set speed for each motor individually (0.0 to 1.0)"""
    left_front_pwm.value = lf
    left_back_pwm.value = lb
    right_front_pwm.value = rf
    right_back_pwm.value = rb
    debug_print(f"Speeds - LF:{int(lf*100)}% LB:{int(lb*100)}% RF:{int(rf*100)}% RB:{int(rb*100)}%")

# -----------------------------
# INDIVIDUAL MOTOR CONTROL
# -----------------------------
def left_back_forward():
    left_back_in1.on()
    left_back_in2.off()

def left_back_backward():
    left_back_in1.off()
    left_back_in2.on()

def left_back_stop():
    left_back_in1.off()
    left_back_in2.off()

def left_front_forward():
    left_front_in1.on()
    left_front_in2.off()

def left_front_backward():
    left_front_in1.off()
    left_front_in2.on()

def left_front_stop():
    left_front_in1.off()
    left_front_in2.off()

def right_front_forward():
    right_front_in1.on()
    right_front_in2.off()

def right_front_backward():
    right_front_in1.off()
    right_front_in2.on()

def right_front_stop():
    right_front_in1.off()
    right_front_in2.off()

def right_back_forward():
    right_back_in1.on()
    right_back_in2.off()

def right_back_backward():
    right_back_in1.off()
    right_back_in2.on()

def right_back_stop():
    right_back_in1.off()
    right_back_in2.off()

# -----------------------------
# BASIC MOTOR FUNCTIONS
# -----------------------------
def stop():
    """Stop all motors"""
    left_back_stop()
    left_front_stop()
    right_front_stop()
    right_back_stop()
    debug_print("STOP")

# -----------------------------
# MECANUM MOVEMENT FUNCTIONS
# -----------------------------
def forward(t):
    """All wheels forward"""
    left_front_forward()
    left_back_forward()
    right_front_forward()
    right_back_forward()
    debug_print("FORWARD")
    sleep(t)
    stop()

def backward(t):
    """All wheels backward"""
    left_front_backward()
    left_back_backward()
    right_front_backward()
    right_back_backward()
    debug_print("BACKWARD")
    sleep(t)
    stop()

def strafe_left(t):
    """Strafe left - LF back, LB forward, RF forward, RB back"""
    left_front_backward()
    left_back_forward()
    right_front_forward()
    right_back_backward()
    debug_print("STRAFE LEFT")
    sleep(t)
    stop()

def strafe_right(t):
    """Strafe right - LF forward, LB back, RF back, RB forward"""
    left_front_forward()
    left_back_backward()
    right_front_backward()
    right_back_forward()
    debug_print("STRAFE RIGHT")
    sleep(t)
    stop()

def spin_left(t):
    """Spin left - left wheels back, right wheels forward"""
    left_front_backward()
    left_back_backward()
    right_front_forward()
    right_back_forward()
    debug_print("SPIN LEFT")
    sleep(t)
    stop()

def spin_right(t):
    """Spin right - left wheels forward, right wheels back"""
    left_front_forward()
    left_back_forward()
    right_front_backward()
    right_back_backward()
    debug_print("SPIN RIGHT")
    sleep(t)
    stop()

def diagonal_forward_left(t):
    """Diagonal forward-left - LB forward, RF forward"""
    left_front_stop()
    left_back_forward()
    right_front_forward()
    right_back_stop()
    debug_print("DIAGONAL FORWARD-LEFT")
    sleep(t)
    stop()

def diagonal_forward_right(t):
    """Diagonal forward-right - LF forward, RB forward"""
    left_front_forward()
    left_back_stop()
    right_front_stop()
    right_back_forward()
    debug_print("DIAGONAL FORWARD-RIGHT")
    sleep(t)
    stop()

def diagonal_backward_left(t):
    """Diagonal backward-left - LF back, RB back"""
    left_front_backward()
    left_back_stop()
    right_front_stop()
    right_back_backward()
    debug_print("DIAGONAL BACKWARD-LEFT")
    sleep(t)
    stop()

def diagonal_backward_right(t):
    """Diagonal backward-right - LB back, RF back"""
    left_front_stop()
    left_back_backward()
    right_front_backward()
    right_back_stop()
    debug_print("DIAGONAL BACKWARD-RIGHT")
    sleep(t)
    stop()

# -----------------------------
# INDIVIDUAL MOTOR TEST FUNCTIONS
# -----------------------------
def test_left_front(t):
    """Test left front motor"""
    print("  Forward...")
    left_front_forward()
    sleep(t)
    left_front_stop()
    sleep(0.5)
    print("  Backward...")
    left_front_backward()
    sleep(t)
    left_front_stop()

def test_left_back(t):
    """Test left back motor"""
    print("  Forward...")
    left_back_forward()
    sleep(t)
    left_back_stop()
    sleep(0.5)
    print("  Backward...")
    left_back_backward()
    sleep(t)
    left_back_stop()

def test_right_front(t):
    """Test right front motor"""
    print("  Forward...")
    right_front_forward()
    sleep(t)
    right_front_stop()
    sleep(0.5)
    print("  Backward...")
    right_front_backward()
    sleep(t)
    right_front_stop()

def test_right_back(t):
    """Test right back motor"""
    print("  Forward...")
    right_back_forward()
    sleep(t)
    right_back_stop()
    sleep(0.5)
    print("  Backward...")
    right_back_backward()
    sleep(t)
    right_back_stop()

# -----------------------------
# CLEANUP FUNCTION
# -----------------------------
def cleanup():
    """Clean up all GPIO resources"""
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
    print("GPIO cleaned up.")

# -----------------------------
# MAIN TEST FUNCTION
# -----------------------------
def main():
    """
    Diagnostic test routine for mecanum wheel car.
    Tests each motor individually then all movement patterns.
    """
    motor_test_duration = 2  # seconds for individual motor tests
    movement_test_duration = 3  # seconds for movement tests
    pause_between = 1
    test_speed = 0.25  # 25% speed for testing
    
    try:
        print("=" * 50)
        print("   MECANUM WHEEL CAR DIAGNOSTIC TEST")
        print("=" * 50)
        print(f"Test speed: {int(test_speed * 100)}%")
        print("Press Ctrl+C at any time to abort\n")
        
        # Set speed for all tests
        set_all_speed(test_speed)
        sleep(2)
        
        # Test 1: Ultrasonic sensor
        print("-" * 40)
        print("TEST 1: Ultrasonic Sensor")
        print("-" * 40)
        for i in range(3):
            dist = get_distance()
            print(f"  Reading {i+1}: {dist} cm")
            sleep(0.5)
        print("Sensor test complete!\n")
        sleep(pause_between)
        
        # # Test 2: Left front motor
        # print("-" * 40)
        # print("TEST 2: Left Front Motor")
        # print("-" * 40)
        # test_left_front(motor_test_duration)
        # print("Left front motor test complete!\n")
        # sleep(pause_between)
        
        # # Test 3: Left back motor
        # print("-" * 40)
        # print("TEST 3: Left Back Motor")
        # print("-" * 40)
        # test_left_back(motor_test_duration)
        # print("Left back motor test complete!\n")
        # sleep(pause_between)
        
        # # Test 4: Right front motor
        # print("-" * 40)
        # print("TEST 4: Right Front Motor")
        # print("-" * 40)
        # test_right_front(motor_test_duration)
        # print("Right front motor test complete!\n")
        # sleep(pause_between)
        
        # # Test 5: Right back motor
        # print("-" * 40)
        # print("TEST 5: Right Back Motor")
        # print("-" * 40)
        # test_right_back(motor_test_duration)
        # print("Right back motor test complete!\n")
        # sleep(pause_between)
        
        # Test 2: Forward
        print("-" * 40)
        print("TEST 2: Forward Movement")
        print("-" * 40)
        forward(movement_test_duration)
        print("Forward test complete!\n")
        sleep(pause_between)
        
        # Test 3: Backward
        print("-" * 40)
        print("TEST 3: Backward Movement")
        print("-" * 40)
        backward(movement_test_duration)
        print("Backward test complete!\n")
        sleep(pause_between)
        
        # Test 4: Strafe left
        print("-" * 40)
        print("TEST 4: Strafe Left")
        print("-" * 40)
        strafe_left(movement_test_duration)
        print("Strafe left test complete!\n")
        sleep(pause_between)
        
        # Test 5: Strafe right
        print("-" * 40)
        print("TEST 5: Strafe Right")
        print("-" * 40)
        strafe_right(movement_test_duration)
        print("Strafe right test complete!\n")
        sleep(pause_between)
        
        # Test 6: Spin left
        print("-" * 40)
        print("TEST 6: Spin Left")
        print("-" * 40)
        spin_left(movement_test_duration)
        print("Spin left test complete!\n")
        sleep(pause_between)
        
        # Test 7: Spin right
        print("-" * 40)
        print("TEST 7: Spin Right")
        print("-" * 40)
        spin_right(movement_test_duration)
        print("Spin right test complete!\n")
        sleep(pause_between)
        
        # Test 8: Diagonal forward-left
        print("-" * 40)
        print("TEST 8: Diagonal Forward-Left")
        print("-" * 40)
        diagonal_forward_left(movement_test_duration)
        print("Diagonal forward-left test complete!\n")
        sleep(pause_between)
        
        # Test 9: Diagonal forward-right
        print("-" * 40)
        print("TEST 9: Diagonal Forward-Right")
        print("-" * 40)
        diagonal_forward_right(movement_test_duration)
        print("Diagonal forward-right test complete!\n")
        sleep(pause_between)
        
        # Test 10: Diagonal backward-left
        print("-" * 40)
        print("TEST 10: Diagonal Backward-Left")
        print("-" * 40)
        diagonal_backward_left(movement_test_duration)
        print("Diagonal backward-left test complete!\n")
        sleep(pause_between)
        
        # Test 11: Diagonal backward-right
        print("-" * 40)
        print("TEST 11: Diagonal Backward-Right")
        print("-" * 40)
        diagonal_backward_right(movement_test_duration)
        print("Diagonal backward-right test complete!\n")
        
        print("=" * 50)
        print("    ALL DIAGNOSTIC TESTS COMPLETED!")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\nTest aborted by user!")
    finally:
        cleanup()


# ---------------------------------------------------------
#         SIMPLE REACTIVE OBSTACLE AVOIDANCE LOOP
# ---------------------------------------------------------
def obstacle_avoidance_loop():
    """Obstacle avoidance using forward movement and turning"""
    obstacle_count = 0
    
    # Set speed for obstacle avoidance (can adjust as needed)
    set_all_speed(0.5)  # 50% speed for obstacle avoidance
    
    try:
        print("Starting movement with obstacle avoidance...")
        debug_print("DEBUG MODE ENABLED - Verbose output on\n")
        
        while True:
            dist = get_distance()
            debug_print(f"Distance: {dist} cm")

            if dist < 20:
                obstacle_count += 1
                
                print(f"[OBSTACLE #{obstacle_count}] Detected at {dist} cm!")
                
                debug_print(f"  -> Timestamp: {__import__('time').strftime('%H:%M:%S')}")
                debug_print(f"  -> Action: Stopping and strafing left")
                debug_print(f"  -> Total obstacles avoided: {obstacle_count}")
                
                stop()
                sleep(0.3)
                strafe_left(0.5)
                
                debug_print(f"  -> Strafe complete, resuming forward motion")
                debug_print("-" * 30)
            else:
                debug_print(f"Path clear ({dist} cm) - moving forward")
                forward(0.2)
                
    except KeyboardInterrupt:
        print("\nStopping program...")
        print(f"Session summary: Avoided {obstacle_count} obstacles")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
    # To run obstacle avoidance instead, comment out main() and uncomment:
    # obstacle_avoidance_loop()