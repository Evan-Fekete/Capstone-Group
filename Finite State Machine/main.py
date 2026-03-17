# Before working start VENV also input: "git pull origin main"
#
# Also if you want to connect to Virtual Environment
# Enter: source /FSMvenv/bin/activate

# Blue Wire: Ground (pin 6), Black Wire: Tx (pin 8), White Wire: Rx (pin 10)

import sys
import os
import json
import math
import time
import serial
import SpeechToText as speech
import app as vision
from enum import Enum

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define interface for talking with ESP32
ser = serial.Serial('/dev/serial0', 9600, timeout=1)

# Define Constants for States for FSM


class state(Enum):
    STARTUP = 1
    TAKE_INSTRUCTION = 2
    FIND_OBJ = 3
    TRAVEL_TO_OBJ = 4
    FIND_USER = 5
    RETURN_OBJ = 6
    PICKUP_OBJ = 7


def printCurrentState(currentState):
    print("Current State: " + str(currentState))


def sendCommand(cmd):
    print("SENDING COMMAND: " + str(cmd))

    ser.write(f'{cmd}\n'.encode())
    # read back a confirmation
    if ser.in_waiting:
        returnValue = ser.readline().decode().strip()
        print("RECEIVED DATA: " + returnValue)
        time.sleep(0.1)
        return returnValue
    else:
        return None


def save_json_response(response_str, filename="object.JSON"):
    """Save LLM JSON response to a file in the script directory."""
    filepath = os.path.join(SCRIPT_DIR, filename)
    try:
        # Parse the JSON string to validate it
        json_data = json.loads(response_str)
        # Write to file
        with open(filepath, 'w') as f:
            json.dump(json_data, f, indent=4)
        print(f"JSON saved to: {filepath}")
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        with open(filepath, 'w') as f:
            f.write(response_str)
        return None


def main():
    print("Starting Raspberry Pi FSM...")

    try:
        currentState = state.STARTUP
        # main match statement used for running code for current state
        while (1):
            match currentState:
                case state.STARTUP:
                    printCurrentState(currentState)

                    # Used to quickly test communication between Pi and ESP32
                    sendCommand("SWIVEL_L")
                    time.sleep(1)
                    sendCommand("STOP")

                    # This vision is call is not used but it activates ultralytics library early on in the code
                    vision.look_around("apple")
                    
                    currentState = state.TRAVEL_TO_OBJ
                    # currentState = state.TAKE_INSTRUCTION
                case state.TAKE_INSTRUCTION:
                    printCurrentState(currentState)
                    # Uncomment to activate recording and transcription
                    # audio = speech.record_audio()
                    # user_input = speech.transcribe_audio(audio)
                    # Uncomment to define user input
                    user_input = "Bring me the mug"
                    # JSON Schema prompt used to return JSON schema for vision system
                    prompt = """You are a robot control agent. Convert user instructions found Real User Input. If parameter is not known then output unknown always display action, object, and color.
                        Schema: action (fetch/place/deliver/stop), object (apple/mug/bottle/shoe)
                        Example:
                        User: bring me the apple
                        JSON: {{"action":"fetch","object":"apple"}}
                        Real User Input:
                        User: {text}
                        JSON:"""
                    formatted = prompt.format(text=user_input)
                    reply = speech.TextToJSON(formatted)
                    print("\nLLM Response:\n", reply)

                    # Save the JSON response to file
                    json_data = save_json_response(reply)
                    print("JSON Data: " + str(json_data))

                    currentState = state.FIND_OBJ
                    time.sleep(5)

                case state.FIND_OBJ:
                    # This state will move robot forward (or some predefined sequence of movments)
                    # Swivel camera nad look for object, if found stop the swiveling save servo position
                    # based on servo position turn car (turn for servoPosition*turnWeight)
                    # After this the robot should ideally be facing the object, now it will move forward

                    # TODO: determine a good turnWeight for the robot
                    printCurrentState(currentState)

                    with open('object.JSON', 'r') as input:
                        query = json.load(input)
                    findObject = query.get("object")

                    # Reset Servo Camera Pan and Tilt positions 
                    sendCommand("SERVO PAN 45")
                    time.sleep(1)
                    sendCommand("SERVO TILT 90")
                    time.sleep(1)
                    sendCommand("SERVO PICK1 90")
                    time.sleep(1)
                    sendCommand("SERVO PICK2 180")
                    time.sleep(1)

                    swivelCount = 0
                    turnCount = 0
                    swivelRight = False

                    while (1):
                        print("Swivel Count: " + str(swivelCount) + " Turn Count: " + str(turnCount) + "\n")
                            
                        if (swivelCount < 60 and swivelRight == True):
                            servoPosition = sendCommand("SWIVEL_R")
                            time.sleep(0.5)
                            swivelCount += 1
                            print("Servo is at " + str(servoPosition))

                        elif (swivelCount < 60 and swivelRight == False):
                            servoPosition = sendCommand("SWIVEL_L")
                            time.sleep(0.5)
                            swivelCount += 1
                            print("Servo is at " + str(servoPosition))

                        elif (swivelCount >= 60 and turnCount < 3):
                            # swivelCount must be above 20 so move forward
                            sendCommand("FORWARD")
                            time.sleep(1)
                            swivelRight = not(swivelRight)
                            swivelCount = 0
                            turnCount += 1
                            print("Servo is at " + servoPosition)

                        elif (swivelCount >= 60 and turnCount >= 3):
                            # swivelCount must be above 20 and moved forward 3 times so turn around
                            sendCommand("LEFT")
                            time.sleep(3)
                            swivelCount = 0
                            turnCount = 0

                        [foundObject, foundBool, bounding_x, bounding_y, offset] = vision.look_around(findObject)

                        if (foundBool == True):
                            print(findObject + " has been found.")

                            turnWeight = 0.005

                            # Turn Object based on servo position and turn weight
                            if (int(servoPosition) < 45):
                                sendCommand("RIGHT")
                                time.sleep((45 - float(servoPosition))*turnWeight)
                                sendCommand("STOP")
                            else:
                                sendCommand("LEFT")
                                time.sleep((float(servoPosition) - 40)*turnWeight)
                                sendCommand("STOP")

                            currentState = state.TRAVEL_TO_OBJ
                            break

                case state.TRAVEL_TO_OBJ:
                    printCurrentState(currentState)
                    # Bools for tilt servo adjustments when approaching the object
                    firstBool = False
                    secondBool = False
                    
                    # load target object
                    with open('object.JSON', 'r') as f:
                        query = json.load(f)

                    target = query.get("object")
                    print(f"Looking for: {target}")

                    if (target == "medicine"):
                        desiredBx = 65
                        desiredBy = 105
                        desiredOffsetMax = 327 # 322 is generally centred for medicine
                        desiredOffsetMin = 317

                    
                    if (target == "mug"):
                        desiredBx = 133
                        desiredBy = 122
                        desiredOffsetMax = 350 # 347 is generally centred for mug
                        desiredOffsetMin = 325
                        #angled
                        desiredBx_ang = 94
                        desiredBy_ang = 119
                        desiredOffsetMax_ang = 335 # 332 is generally centred for angled mug
                        desiredOffsetMin_ang = 322

                    if (target == "remote"):
                        desiredBx = 155
                        desiredBy = 35
                        desiredOffsetMax = 333 # 330 is generally centred for remote
                        desiredOffsetMin = 320
                        #angled
                        # desiredBx_ang = 94
                        # desiredBy_ang = 119
                        # desiredOffsetMax_ang = 335 # 330 is generally centred for angled remote
                        # desiredOffsetMin_ang = 322

                    if (target == "shoe"):
                        desiredBx = 132
                        desiredBy = 118
                        desiredOffsetMax = 341 # 338 is generally centred for shoe
                        desiredOffsetMin = 328
                        #angled
                        desiredBx_ang = 138
                        desiredBy_ang = 102
                        desiredOffsetMax_ang = 336 # 333 is generally centred for angled shoe
                        desiredOffsetMin_ang = 323

                    if (target == "user"):
                        desiredBx = 114
                        desiredBy = 198
                        desiredOffsetMax = 333 # 330 is generally centred for user
                        desiredOffsetMin = 320
                        #angled
                        # desiredBx_ang = 138
                        # desiredBy_ang = 102
                        # desiredOffsetMax_ang = 336 # 333 is generally centred for angled shoe
                        # desiredOffsetMin_ang = 323


                    sendCommand("SERVO TILT 90")
                    time.sleep(2)
                    sendCommand("SERVO PAN 45")
                    time.sleep(3)

                    # Look at bounding box to see how far/off target the robot is pointings
                    result = vision.look_around(target)
                    obj, found, bx, by , offset_x= result
                    print(f"before while bounding box x: {bx}")
                    print(f"before while bounding box y: {by}")
                    print(f"before while offset: {offset_x}")

                    while (bx < desiredBx and by < desiredBy):
                        r = vision.look_around(target)
                        obj, found, bx, by , offset_x = r
                        print(f"bounding box x: {bx}")
                        print(f"bounding box y: {by}")
                        print(f"offset: {offset_x}")

                        if ((bx > 70 or by > 70) and firstBool == False):
                            sendCommand("SERVO TILT 100")
                            time.sleep(5)
                            firstBool = True

                        elif ((bx > 90 or by > 90) and secondBool == False):
                            time.sleep(1)
                            secondBool = True

                        elif (offset_x < desiredOffsetMin - 30):
                            sendCommand("M_LEFT")
                            time.sleep(1)
                            print("Moving Left")

                        elif (desiredOffsetMax + 30 < offset_x ):
                            sendCommand("M_RIGHT")
                            time.sleep(1)
                            print("Moving Right")

                        elif (offset_x < desiredOffsetMin):
                            sendCommand("S_LEFT")
                            time.sleep(1)
                            print("Moving left")

                        elif (desiredOffsetMax < offset_x):
                            sendCommand("S_RIGHT")
                            time.sleep(1)
                            print("Moving Right")

                        elif (secondBool == True):
                            sendCommand("SLOW_FORWARD")
                            time.sleep(2)
                            print("Moving forward slowly")
                        else:
                            sendCommand("FORWARD")
                            time.sleep(1)
                            print("Moving forward")
                    sendCommand("STOP")

                    time.sleep(3)
                    currentState = state.PICKUP_OBJ
                case state.FIND_USER:
                    # This state will move robot forward (or some predefined sequence of movments)
                    # Swivel camera and look for the user, if found stop the swiveling save servo position
                    # based on servo position turn car (turn for servoPosition*turnWeight)
                    # After this the robot should ideally be facing the the user, now it will move forward

                    printCurrentState(currentState)

                    findObject = "user"

                    # Reset Servo Camera Pan and Tilt positions 
                    sendCommand("SERVO PAN 0")
                    time.sleep(1)
                    sendCommand("SERVO TILT 90")
                    time.sleep(1)
                    sendCommand("SERVO PICK1 90")
                    time.sleep(1)
                    sendCommand("SERVO PICK2 180")
                    time.sleep(1)

                    swivelCount = 0
                    turnCount = 0
                    swivelRight = False

                    while (1):
                        print("Swivel Count: " + str(swivelCount) + " Turn Count: " + str(turnCount) + "\n")
                            
                        if (swivelCount < 60 and swivelRight == True):
                            servoPosition = sendCommand("SWIVEL_R")
                            time.sleep(0.5)
                            swivelCount += 1
                            print("Servo is at " + str(servoPosition))

                        elif (swivelCount < 60 and swivelRight == False):
                            servoPosition = sendCommand("SWIVEL_L")
                            time.sleep(0.5)
                            swivelCount += 1
                            print("Servo is at " + str(servoPosition))

                        elif (swivelCount >= 60 and turnCount < 3):
                            # swivelCount must be above 20 so move forward
                            sendCommand("FORWARD")
                            time.sleep(1)
                            swivelRight = not(swivelRight)
                            swivelCount = 0
                            turnCount += 1
                            print("Servo is at " + servoPosition)

                        elif (swivelCount >= 60 and turnCount >= 3):
                            # swivelCount must be above 20 and moved forward 3 times so turn around
                            sendCommand("LEFT")
                            time.sleep(3)
                            swivelCount = 0
                            turnCount = 0

                        [foundObject, foundBool, bounding_x, bounding_y, offset] = vision.look_around(findObject)

                        if (foundBool == True):
                            print(findObject + " has been found.")

                            turnWeight = 0.005

                            # Turn Object based on servo position and turn weight
                            if (int(servoPosition) < 45):
                                sendCommand("RIGHT")
                                time.sleep((45 - float(servoPosition))*turnWeight)
                                sendCommand("STOP")
                            else:
                                sendCommand("LEFT")
                                time.sleep((float(servoPosition) - 45)*turnWeight)
                                sendCommand("STOP")

                    time.sleep(5)

                case state.RETURN_OBJ:
                    printCurrentState(currentState)

                    firstBool = False
                    secondBool = False
                    
                    target = "user"
                    print(f"Looking for: {target}")

                    sendCommand("SERVO TILT 90")
                    time.sleep(2)
                    sendCommand("SERVO PAN 45")
                    time.sleep(3)

                    # Look at bounding box to see how far/off target the robot is pointings
                    result = vision.look_around(target)
                    obj, found, bx, by , offset_x= result
                    print(f"before while bounding box x: {bx}")
                    print(f"before while bounding box y: {by}")
                    print(f"before while offset: {offset_x}")

                    while (bx < 105 and by < 105):
                        r = vision.look_around(target)
                        obj, found, bx, by , offset_x = r
                        print(f"bounding box x: {bx}")
                        print(f"bounding box y: {by}")
                        print(f"offset: {offset_x}")

                        if ((bx > 50 or by > 50) and firstBool == False):
                            sendCommand("SERVO TILT 100")
                            time.sleep(5)
                            firstBool = True

                        if ((bx > 70 or by > 70) and secondBool == False):
                            sendCommand("SERVO TILT 110")
                            time.sleep(5)
                            secondBool = True

                        if (offset_x < 300): # 322 is generally completely centred for medicine bottle
                            sendCommand("S_LEFT")
                            time.sleep(0.1)
                            print("Moving left")

                        elif (340 < offset_x):
                            sendCommand("S_RIGHT")
                            time.sleep(0.1)
                            print("Moving Right")

                        else:
                            sendCommand("FORWARD")
                            time.sleep(0.1)
                            print("Moving forward")
                    sendCommand("STOP")

                    time.sleep(3)
                    currentState = state.TAKE_INSTRUCTION

                case state.PICKUP_OBJ:
                    printCurrentState(currentState)

                    # sendCommand("PICKUP")
                    time.sleep(10)

                    currentState = state.PICKUP_OBJ

                case _:
                    print("Current State: UNKNOWN STATE")

    except KeyboardInterrupt:
        print("Running interuppted by User")
    finally:
        sendCommand("STOP")
        print("ENDING...")


if __name__ == "__main__":
    main()
