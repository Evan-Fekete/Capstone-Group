/****************************************************
 * ESP32 DevKit V1 - Mecanum / Differential Drive Motor Control
 * With UART command interface for Raspberry Pi
 * 
 * Compatible with: ESP32 DevKit V1 (DOIT / ESP-WROOM-32)
 * PWM channels: separate for each motor (best practice)
 * Speed range: -1023 to 1023 (10-bit resolution)
 ****************************************************/

// =====================
// PIN DEFINITIONS - Safe for ESP32 DevKit V1
// =====================
#define PWM_FREQ  5000
#define PWM_RES   10          // 0-1023 range

// LEFT SIDE
#define LEFT_FRONT_EN   25    // PWM
#define LEFT_FRONT_IN1  26
#define LEFT_FRONT_IN2  27
#define LEFT_FRONT_CH   0

#define LEFT_REAR_EN    33    // PWM
#define LEFT_REAR_IN1   32
#define LEFT_REAR_IN2   14
#define LEFT_REAR_CH    1

// RIGHT SIDE
#define RIGHT_FRONT_EN  18    // PWM
#define RIGHT_FRONT_IN1 19
#define RIGHT_FRONT_IN2 21
#define RIGHT_FRONT_CH  2

#define RIGHT_REAR_EN   5     // PWM
#define RIGHT_REAR_IN1  17
#define RIGHT_REAR_IN2  16
#define RIGHT_REAR_CH   3

// =====================
// UART FROM RASPBERRY PI
// =====================
HardwareSerial piSerial(1);
#define PI_RX 16  // ESP32 RX from Pi TX
#define PI_TX 17  // ESP32 TX to Pi RX

// =====================
// MOTOR CONTROL FUNCTIONS
// =====================
void setMotor(int channel, int in1, int in2, int speed) {
  speed = constrain(speed, -1023, 1023);
  bool forward = (speed >= 0);
  int absSpeed = abs(speed);

  digitalWrite(in1, forward);
  digitalWrite(in2, !forward);
  ledcWrite(channel, absSpeed);
}

void setLeftSide(int speed) {
  setMotor(LEFT_FRONT_CH, LEFT_FRONT_IN1, LEFT_FRONT_IN2, speed);
  setMotor(LEFT_REAR_CH,  LEFT_REAR_IN1,  LEFT_REAR_IN2,  speed);
}

void setRightSide(int speed) {
  setMotor(RIGHT_FRONT_CH, RIGHT_FRONT_IN1, RIGHT_FRONT_IN2, speed);
  setMotor(RIGHT_REAR_CH,  RIGHT_REAR_IN1,  RIGHT_REAR_IN2,  speed);
}

void stopAllMotors() {
  setLeftSide(0);
  setRightSide(0);
}

// High-level commands
void driveForward(int speed = 600) {
  setLeftSide(speed);
  setRightSide(speed);
}

void driveBackward(int speed = 600) {
  setLeftSide(-speed);
  setRightSide(-speed);
}

void turnLeft(int speed = 600) {
  setLeftSide(-speed);
  setRightSide(speed);
}

void turnRight(int speed = 600) {
  setLeftSide(speed);
  setRightSide(-speed);
}

// =====================
// COMMAND HANDLER
// =====================
void executeCommand(String cmd) {
  Serial.println("Received: " + cmd);

  if (cmd == "FORWARD") {
    driveForward(600);
    piSerial.println("OK:FORWARD");
  }
  else if (cmd == "BACKWARD") {
    driveBackward(600);
    piSerial.println("OK:BACKWARD");
  }
  else if (cmd == "LEFT") {
    turnLeft(600);
    piSerial.println("OK:LEFT");
  }
  else if (cmd == "RIGHT") {
    turnRight(600);
    piSerial.println("OK:RIGHT");
  }
  else if (cmd == "STOP") {
    stopAllMotors();
    piSerial.println("OK:STOP");
  }
  else if (cmd == "SEARCH") {
    driveForward(400);  // slow search speed
    piSerial.println("OK:SEARCH");
  }
  else if (cmd == "PICKUP") {
    stopAllMotors();
    // TODO: add servo/gripper code here
    piSerial.println("OK:PICKUP");
  }
  else {
    piSerial.println("ERR:UNKNOWN");
  }
}

// =====================
// SETUP
// =====================
void setup() {
  Serial.begin(115200);
  piSerial.begin(9600, SERIAL_8N1, PI_RX, PI_TX);
  delay(200);

  Serial.println("\nESP32 Robot - UART Command Mode");
  Serial.println("Pins used:");
  Serial.printf("Left Front: EN=%d IN1=%d IN2=%d\n", LEFT_FRONT_EN, LEFT_FRONT_IN1, LEFT_FRONT_IN2);
  Serial.printf("Left Rear:  EN=%d IN1=%d IN2=%d\n", LEFT_REAR_EN,  LEFT_REAR_IN1,  LEFT_REAR_IN2);
  Serial.printf("Right Front: EN=%d IN1=%d IN2=%d\n", RIGHT_FRONT_EN, RIGHT_FRONT_IN1, RIGHT_FRONT_IN2);
  Serial.printf("Right Rear:  EN=%d IN1=%d IN2=%d\n", RIGHT_REAR_EN,  RIGHT_REAR_IN1,  RIGHT_REAR_IN2);
  Serial.printf("Pi UART: RX=%d TX=%d\n", PI_RX, PI_TX);

  // Direction pins
  pinMode(LEFT_FRONT_IN1, OUTPUT);
  pinMode(LEFT_FRONT_IN2, OUTPUT);
  pinMode(LEFT_REAR_IN1,  OUTPUT);
  pinMode(LEFT_REAR_IN2,  OUTPUT);
  pinMode(RIGHT_FRONT_IN1, OUTPUT);
  pinMode(RIGHT_FRONT_IN2, OUTPUT);
  pinMode(RIGHT_REAR_IN1,  OUTPUT);
  pinMode(RIGHT_REAR_IN2,  OUTPUT);

  // PWM setup
  ledcSetup(LEFT_FRONT_CH, PWM_FREQ, PWM_RES);
  ledcSetup(LEFT_REAR_CH,  PWM_FREQ, PWM_RES);
  ledcSetup(RIGHT_FRONT_CH, PWM_FREQ, PWM_RES);
  ledcSetup(RIGHT_REAR_CH,  PWM_FREQ, PWM_RES);

  ledcAttachPin(LEFT_FRONT_EN,  LEFT_FRONT_CH);
  ledcAttachPin(LEFT_REAR_EN,   LEFT_REAR_CH);
  ledcAttachPin(RIGHT_FRONT_EN, RIGHT_FRONT_CH);
  ledcAttachPin(RIGHT_REAR_EN,  RIGHT_REAR_CH);

  stopAllMotors();
  Serial.println("Ready for Pi commands.");
}

// =====================
// MAIN LOOP
// =====================
void loop() {
  if (piSerial.available()) {
    String cmd = piSerial.readStringUntil('\n');
    cmd.trim();
    executeCommand(cmd);
  }
}
