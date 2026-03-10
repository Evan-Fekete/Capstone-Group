# Before working start VENV also input: "git pull origin main"
#
# Also if you want to connect to Virtual Environment
# Enter: source /FSMvenv/bin/activate

# Blue Wire: Ground (pin 6), White Wire: Rx (pin 8), Black Wire: Tx (pin 10)

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
                    
                    currentState = state.TAKE_INSTRUCTION
                case state.TAKE_INSTRUCTION:
                    printCurrentState(currentState)
                    # Uncomment to activate recording and transcription
                    # audio = speech.record_audio()
                    # user_input = speech.transcribe_audio(audio)
                    # Uncomment to define user input
                    user_input = "Bring me the red apple"
                    # JSON Schema prompt used to return JSON schema for vision system
                    prompt = """You are a robot control agent. Convert user instructions found Real User Input. If parameter is not known then output unknown always display action, object, and color.
                        Schema: action (fetch/place/deliver/stop), object (apple/mug/bottle/shoe), color (red/blue/green/white/unknown)
                        Example:
                        User: bring me the red apple
                        JSON: {{"action":"fetch","object":"apple","color":"red"}}
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

                    # TODO: Work on logic for finding the object,
                    # TODO: determine a good turnWeight for the robot,
                    printCurrentState(currentState)

                    with open('object.JSON', 'r') as input:
                        query = json.load(input)
                    findObject = query.get("object")

                    # Reset Servo Camera Pan and Tilt positions 
                    sendCommand("SERVO PAN 0")
                    time.sleep(5)
                    sendCommand("SERVO TILT 80")
                    time.sleep(5)
                    sendCommand("SERVO PICK1 90")
                    time.sleep(5)
                    sendCommand("SERVO PICK2 90")
                    time.sleep(5)

                    swivelCount = 0
                    turnCount = 0
                    swivelRight = False

                    while (1):
                        print("Swivel Count: " + str(swivelCount) + " Turn Count: " + str(turnCount) + "\n")
                            
                        if (swivelCount < 20 and swivelRight == True):
                            servoPosition = sendCommand("SWIVEL_R")
                            time.sleep(0.5)
                            swivelCount += 1
                            print("Servo is at " + servoPosition)

                        elif (swivelCount < 20 and swivelRight == False):
                            servoPosition = sendCommand("SWIVEL_L")
                            time.sleep(0.5)
                            swivelCount += 1
                            print("Servo is at " + servoPosition)

                        elif (swivelCount >= 3 and turnCount < 3):
                            # swivelCount must be above 20 so move forward
                            sendCommand("FORWARD")
                            time.sleep(1)
                            swivelRight = not(swivelRight)
                            swivelCount = 0
                            turnCount += 1
                            print("Servo is at " + servoPosition)

                        elif (swivelCount >= 3 and turnCount >= 3):
                            # swivelCount must be above 20 and moved forward 3 times so turn around
                            sendCommand("LEFT")
                            time.sleep(3)
                            swivelCount = 0
                            turnCount = 0

                        [findObject, foundBool, bounding_x, bounding_y] = vision.look_around(findObject)
                        print(foundBool)

                        if (foundBool == True):
                            print(findObject + " has been found.")

                            turnWeight = 0.1

                            # Turn Object based on servo position and turn weight
                            if (int(servoPosition) < 45):
                                sendCommand("LEFT")
                                time.sleep(float(servoPosition)*turnWeight)
                                sendCommand("STOP")
                            else:
                                sendCommand("RIGHT")
                                time.sleep(float(servoPosition)*turnWeight)
                                sendCommand("STOP")

                            currentState = state.TRAVEL_TO_OBJ
                            break

                case state.TRAVEL_TO_OBJ:
                    printCurrentState(currentState)
                    # TODO: Add logic for moving towards object and checking if object is in view if not go back state
                    [bounding_x, bounding_y] = vision.dimenisons(
                        findObject, class_names, x1, y1, x2, y2)
                    while (bounding_x < 50 and bounding_y < 50):
                        sendCommand("FORWARD")
                    time.sleep(3)
                case state.FIND_USER:
                    printCurrentState(currentState)
                    # TODO Use similar code for FIND_OBJ to find user

                case state.RETURN_OBJ:
                    printCurrentState(currentState)
                    # TODO User similar code for TRAVEL_TO_OBJ for returning object

                case state.PICKUP_OBJ:
                    printCurrentState(currentState)

                    sendCommand("PICKUP")
                    time.sleep(10)

                    currentState = state.FIND_USER

                case _:
                    print("Current State: UNKNOWN STATE")

    except KeyboardInterrupt:
        print("Running interuppted by User")
    finally:
        print("ENDING...")


if __name__ == "__main__":
    main()
