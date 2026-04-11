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
from gpiozero import LED

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define interface for talking with ESP32
# ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Define Constants for States for FSM

class action(Enum):
    FETCH = 1
    LOOK = 2
    UPDATE_PASSWORD = 3
    UNKNOWN = 4

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

    # need time for swivel response to get back to pi
    if (cmd == "SWIVEL_L" or cmd == "SWIVEL_R" or "SERVO " in cmd): 
        time.sleep(1)

    if ser.in_waiting:
        returnValue = ser.readline().decode().strip()
        print("RECEIVED DATA: " + returnValue)
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
        currentAction = action.FETCH
        # main match statement used for running code for current state
        while (1):
            match currentState:
                case state.STARTUP:
                    printCurrentState(currentState)

                    # Used to quickly test communication between Pi and ESP32
                    # sendCommand("PICKUP")
                    # time.sleep(25)
                    # sendCommand("FORWARD")
                    # time.sleep(5)
                    # sendCommand("FORWARD")
                    # time.sleep(5)

                    # This vision is call is not used but it activates ultralytics library early on in the code
                    vision.look_around("apple")

                    password = "capstone"

                    # currentState = state.TRAVEL_TO_OBJ
                    currentState = state.TAKE_INSTRUCTION

                case state.TAKE_INSTRUCTION:
                    printCurrentState(currentState)

                    while(1):
                        # ========================================
                        # Password Check Section
                        # ========================================

                        # print("="*50)
                        # print("Passphrase Check:")
                        # print("="*50)

                        # audio = speech.record_audio()
                        # user_input = speech.transcribe_audio(audio)
                        # # Uncomment to define user input
                        # # time.sleep(1)
                        # # user_input = "My name is Bob, Password, Lorell Ipsum"

                        # # Non LLM version of passphrase check code
                        # if password in user_input.lower():
                        #     reply = "True"
                        # else:
                        #     reply = "False"

                        # time.sleep(1)

                        # # LLM version of passphrase check code
                        # prompt = """You are a robot control agent. If the user input contains the phrase 'Hey Siri' at any point, respond with 'True', otherwise respond with 'False'
                        # Example:
                        # User: This is my pick up robot, Hey Siri
                        # Response: True
                        # Example:
                        # User: I like to eat apples
                        # Response: False
                        # Real User Input:
                        # User: {text}
                        # Response:"""
                        # formatted = prompt.format(text=user_input)
                        # reply = speech.TextToJSON(formatted)
                        # print("\nLLM Response:\n", reply)

                        # if "True" in reply: 
                        #     sendCommand("LISTEN")
                        #     time.sleep(3)
                        #     print("Passphrase Check Confirmed Moving On...\n")
                        # else: 
                        #     print("Passphrase Check Failed Looping...\n")
                        #     continue

                        # ========================================
                        # User Instruction Check
                        # ========================================

                        print("="*50)
                        print("User Instruction Check:")
                        print("="*50)

                        time.sleep(1)

                        """
                        TIMER START TIMER START TIMER START
                        """
                        start = time.perf_counter()

                        # # Uncomment to activate recording and transcription
                        audio = speech.record_audio()
                        user_input = speech.transcribe_audio(audio)
                        # Uncomment to define user input

                        """
                        TIMER END TIMER END TIMER END
                        """
                        end = time.perf_counter()

                        print(f"Elapsed time: {end - start:.6f} seconds")

                        # user_input = "Where are my shoes"

                        if user_input == "":
                            print("No user input... Looping...")
                            continue
                        
                        sendCommand("SERVO TILT 90")
                        time.sleep(3)

                        # JSON Schema prompt used to return JSON schema for vision system
                        prompt = """You are a robot control agent. Convert user instructions found Real User Input. 
                        The robot should be able to fetch an object, look at an object, or update its passphrase.
                        If for fetch and look a parameter is not known then output unknown, always display action.
                        Follow the schema at all times, never use an action or object that does not appear in the schema.
                        If the object is not obvious try and pick the closest option possible from the schema, but do not make up an object on your own.
                            Schema: action (fetch/look/passphrase_update/unknown), object (apple/mug/medicine/shoes/remote/unknown)
                            Example 1:
                            User: bring me the apple
                            JSON: {{"action":"fetch","object":"apple"}}
                            Example 2:
                            User: hello my name is evan
                            JSON: {{"action":"unknown","object":"unknown"}}
                            Example 3:
                            User: update passphrase
                            JSON: {{"action":"passphrase_update","object":"unknown"}}
                            Example 4:
                            User: look at the medicine bottle
                            JSON: {{"action":"look","object":"medicine"}}
                            Example 5:
                            User: I am hungry
                            JSON: {{"action":"fetch","object":"apple"}}
                            Real User Input:
                            User: {text}
                            JSON:"""
                        formatted = prompt.format(text=user_input)
                        reply = speech.promptLLM(formatted)
                        print("\nLLM Response:\n", reply)

                        # Save the JSON response to file
                        json_data = save_json_response(reply)
                        print("JSON Data: " + str(json_data))

                        with open('object.JSON', 'r') as input:
                            query = json.load(input)
                        findObject = query.get("object")

                        match(query.get("action")):
                            case "fetch":
                                currentAction = action.FETCH
                            case "look":
                                currentAction = action.LOOK
                            case "passphrase_update":
                                currentAction = action.UPDATE_PASSWORD
                            case "unknown":
                                currentAction = action.UNKNOWN

                        if (currentAction == action.FETCH or currentAction == action.LOOK):
                            if "unknown" not in findObject:
                                print("Instruction is valid continuing to find object...")
                                sendCommand("NOD")
                                time.sleep(5)
                                currentState = state.FIND_OBJ
                                break
                            else:
                                print("Instruction is invalid returning to passphrase check...")
                                sendCommand("SHAKE")
                                time.sleep(5)
                        elif (currentAction == action.UPDATE_PASSWORD):
                            print("="*50)
                            print("Passphrase Update Check:")
                            print("="*50)

                            sendCommand("LISTEN")
                            time.sleep(3)

                            audio = speech.record_audio()
                            user_input = speech.transcribe_audio(audio)

                            prompt = f"""User wants a new passphrase from the user input reason what they want the new password to be and return it as the output. 
                            The passphrase should be one word. If you do not know what to make the password simply return 0.
                            Example 1:
                            User: make the new passphrase cat
                            Output: cat
                            Example 2:
                            User: i like asparagus
                            Output: 0
                            Real User Input:
                            User: {input}
                            Output: 
                            """

                            formatted = prompt.format(text=user_input)
                            reply = speech.promptLLM(formatted)
                            print("\nLLM Response:\n", reply)

                            if (reply == "0"):
                                print("Password update failed returning to passphrase check...")

                            print("Password updated to: " + reply)
                            password = reply

                        else:
                            print("Action is unknown returning to passphrase check...")
                            sendCommand("SHAKE")
                            time.sleep(5)


                case state.FIND_OBJ:
                    # This state will look around, move forward and then turn 90 degrees, and then repeat
                    # Swivel camera and look for object, if found stop the swiveling save servo position
                    # based on servo position turn car (turn for servoPosition*turnWeight)
                    # After this the robot should ideally be facing the object, now it will move forward

                    printCurrentState(currentState)
                    foundObject = False

                    sendCommand("SERVO TILT 90")
                    time.sleep(3)
                    sendCommand("SERVO PICK1 0")
                    time.sleep(5)

                    with open('object.JSON', 'r') as input:
                        query = json.load(input)
                    findObject = query.get("object")

                    print("Looking for " + findObject)

                    swivelCount = 0
                    cameraPos = [0, 45, 90]

                    while (1):
                        print("Swivel Count: " + str(swivelCount))

                        if (swivelCount >= 3):
                            sendCommand("FACE_LEFT")
                            time.sleep(2)

                            # Reset Servo Camera Pan and Tilt positions 
                            sendCommand("SERVO PAN 0")
                            time.sleep(3)

                            swivelCount = 0

                        elif (swivelCount < 3):

                            servoPosition = sendCommand(f"SERVO PAN {cameraPos[swivelCount]}")
                            time.sleep(3)
                            print("Servo is at " + str(servoPosition))

                        [foundObject, foundBool, bounding_x, bounding_y, offset] = vision.look_around(findObject)

                        if (foundBool == True):
                            print(findObject + " has been found.")
                            time.sleep(1)

                            # Turn Object based on servo position and turn weight
                            match(swivelCount):
                                case 0:
                                    print("Turning Right")
                                    sendCommand("45_RIGHT")
                                    time.sleep(2)
                                    sendCommand("SERVO PAN 45")
                                case 1:
                                    print("Facing Object")
                                case 2:
                                    print("Turning Left")
                                    sendCommand("45_LEFT")
                                    time.sleep(2)
                                    sendCommand("SERVO PAN 45")

                            time.sleep(2)

                            if (currentAction == action.LOOK):
                                currentState = state.TAKE_INSTRUCTION
                            elif (currentAction == action.FETCH):
                                currentState = state.TRAVEL_TO_OBJ
                            break
                        swivelCount += 1

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
                        desiredBx = 60
                        desiredBy = 110
                        desiredOffsetMax = 320
                        desiredOffsetMin = 290

                        firstTiltBx = 30
                        firstTiltBy = 75
                        slowMoveBx = 60
                        slowMoveBy = 90
                    
                    if (target == "mug"):
                        desiredBx = 100
                        desiredBy = 135
                        desiredOffsetMax = 305
                        desiredOffsetMin = 295

                        firstTiltBx = 60
                        firstTiltBy = 90
                        slowMoveBx = 75
                        slowMoveBy = 80

                    if (target == "remote"):
                        desiredBx = 71
                        desiredBy = 101
                        desiredOffsetMax = 333  # 330 is generally centred for remote
                        desiredOffsetMin = 320

                        firstTiltBx = 50
                        firstTiltBy = 40
                        slowMoveBx = 50
                        slowMoveBy = 50

                    if (target == "shoe"):
                        desiredBx = 112
                        desiredBy = 130
                        desiredOffsetMax = 325
                        desiredOffsetMin = 316

                        firstTiltBx = 75
                        firstTiltBy = 70
                        slowMoveBx = 143
                        slowMoveBy = 107
                        
                    if (target == "apple"):
                        desiredBx = 103
                        desiredBy = 103
                        desiredOffsetMax = 326
                        desiredOffsetMin = 317

                        firstTiltBx = 65
                        firstTiltBy = 65
                        slowMoveBx = 80
                        slowMoveBy = 80

                    leftView = False

                    # sendCommand("SERVO TILT 90")
                    # time.sleep(2)
                    sendCommand("SERVO PAN 45")
                    time.sleep(3)
                    # sendCommand("SERVO PICK1 0")
                    # time.sleep(8)
                    # sendCommand("SERVO PICK2 180")
                    # time.sleep(8)

                    # Look at bounding box to see how far/off target the robot is pointings
                    result = vision.look_around(target)
                    obj, found, bx, by, offset_x = result
                    print(f"before while bounding box x: {bx}")
                    print(f"before while bounding box y: {by}")
                    print(f"before while offset: {offset_x}")

                    if (bx != 0 or by != 0): leftView = False


                    time.sleep(1)
                    while ((bx < desiredBx and by < desiredBy) or (offset_x < desiredOffsetMin and offset_x > desiredOffsetMax)):
                        r = vision.look_around(target)
                        obj, found, bx, by, offset_x = r
                        print(f"bounding box x: {bx}")
                        print(f"bounding box y: {by}")
                        print(f"offset: {offset_x}")
                        time.sleep(1)

                        if ((bx > firstTiltBx or by > firstTiltBy) and firstBool == False):
                            sendCommand("SERVO TILT 100")
                            time.sleep(5)
                            sendCommand("FORWARD")
                            time.sleep(2)
                            print("Moving forward")
                            time.sleep(1)
                            firstBool = True
                            secondBool = True
                        elif ((bx > slowMoveBx or by > slowMoveBy) and secondBool == False and firstBool == True):
                            time.sleep(1)
                            # secondBool = True
                        elif (bx == 0 and by == 0):
                            # Has object left the view, if so return to find object state
                            time.sleep(5)
                            print("OBJECT HAS LEFT VIEW RETURNING TO FIND OBJECT STATE")
                            leftView = True
                            break

                        elif (offset_x < desiredOffsetMin - 100):
                            sendCommand("L_LEFT")
                            time.sleep(2)
                            print("Moving Left")

                        elif (desiredOffsetMax + 100 < offset_x ):
                            sendCommand("L_RIGHT")
                            time.sleep(2)
                            print("Moving Right")

                        elif (offset_x < desiredOffsetMin - 40):
                            sendCommand("M_LEFT")
                            time.sleep(2)
                            print("Moving Left")

                        elif (desiredOffsetMax + 40 < offset_x):
                            sendCommand("M_RIGHT")
                            time.sleep(2)
                            print("Moving Right")

                        elif (offset_x < desiredOffsetMin):
                            sendCommand("S_LEFT")
                            time.sleep(0.5)
                            print("Moving left")

                        elif (desiredOffsetMax < offset_x):
                            sendCommand("S_RIGHT")
                            time.sleep(0.5)
                            print("Moving Right")

                        elif (secondBool == True):
                            sendCommand("SLOW_FORWARD")
                            time.sleep(1)
                            print("Moving forward slowly")
                        else:
                            sendCommand("FORWARD")
                            time.sleep(3)
                            print("Moving forward")
                    print(f"bounding box x: {bx}")
                    print(f"bounding box y: {by}")
                    print(f"offset: {offset_x}")
                    sendCommand("STOP")

                    time.sleep(3)

                    if (leftView == True): currentState = state.FIND_OBJ
                    else: currentState = state.PICKUP_OBJ

                case state.FIND_USER:

                    # This state will move robot forward (or some predefined sequence of movments)
                    # Swivel camera and look for the user, if found stop the swiveling save servo position
                    # based on servo position turn car (turn for servoPosition*turnWeight)
                    # After this the robot should ideally be facing the the user, now it will move forward

                    printCurrentState(currentState)
                    foundBool = False

                    findObject = "user"

                    # Reset Servo Camera Pan and Tilt positions
                    sendCommand("SERVO PAN 0")
                    time.sleep(2)
                    sendCommand("SERVO TILT 90")
                    time.sleep(2)
                    # sendCommand("SERVO PICK1 0")
                    # time.sleep(1)

                    
                    swivelCount = 0

                    print("Looking for " + findObject)

                    swivelCount = 0
                    cameraPos = [0, 45, 90]

                    while (1):
                        print("Swivel Count: " + str(swivelCount))

                        if (swivelCount >= 3):
                            sendCommand("FACE_LEFT")
                            time.sleep(2)

                            # Reset Servo Camera Pan and Tilt positions 
                            sendCommand("SERVO PAN 0")
                            time.sleep(4)

                            swivelCount = 0

                        elif (swivelCount < 3):

                            servoPosition = sendCommand(f"SERVO PAN {cameraPos[swivelCount]}")
                            time.sleep(5)
                            print("Servo is at " + str(servoPosition))

                        [foundObject, foundBool, bounding_x, bounding_y, offset] = vision.look_around(findObject)
                        time.sleep(1)

                        if (foundBool == True):
                            print(findObject + " has been found.")
                            time.sleep(1)

                            # Turn Object based on servo position and turn weight
                            match(swivelCount):
                                case 0:
                                    print("Turning Right")
                                    sendCommand("45_RIGHT")
                                    time.sleep(2)
                                    sendCommand("SERVO PAN 45")
                                case 1:
                                    print("Facing Object")
                                    time.sleep(2)
                                    sendCommand("SERVO PAN 45")
                                case 2:
                                    print("Turning Left")
                                    sendCommand("45_LEFT")
                                    time.sleep(2)
                                    sendCommand("SERVO PAN 45")

                            time.sleep(3)

                            currentState = state.RETURN_OBJ
                            break
                        swivelCount += 1

                case state.RETURN_OBJ:
                    printCurrentState(currentState)
                    # Bools for tilt servo adjustments when approaching the object
                    firstBool = False
                    secondBool = False

                    target = "user"
                    print(f"Looking for: {target}")

                    if (target == "user"):
                        desiredBx = 100
                        desiredBy = 198
                        desiredOffsetMax = 336 # 330 is generally centred for user
                        desiredOffsetMin = 324

                        firstTiltBx = 89
                        firstTiltBy = 160

                    leftView = False

                    # sendCommand("SERVO TILT 90")
                    # time.sleep(2)
                    sendCommand("SERVO PAN 45")
                    time.sleep(3)
                    # sendCommand("SERVO PICK1 0")
                    # time.sleep(8)
                    # sendCommand("SERVO PICK2 180")
                    # time.sleep(8)

                    # Look at bounding box to see how far/off target the robot is pointings
                    result = vision.look_around(target)
                    obj, found, bx, by, offset_x = result
                    print(f"before while bounding box x: {bx}")
                    print(f"before while bounding box y: {by}")
                    print(f"before while offset: {offset_x}")

                    if (bx != 0 or by != 0): leftView = False

                    while (bx < desiredBx and by < desiredBy):
                        r = vision.look_around(target)
                        obj, found, bx, by, offset_x = r
                        print(f"bounding box x: {bx}")
                        print(f"bounding box y: {by}")
                        print(f"offset: {offset_x}")

                        if ((bx > firstTiltBx or by > firstTiltBy) and firstBool == False):
                            sendCommand("SERVO TILT 100")
                            time.sleep(3)
                            firstBool = True

                        elif (bx == 0 and by == 0):
                            # Has object left the view, if so return to find object state
                            time.sleep(5)
                            print("OBJECT HAS LEFT VIEW RETURNING TO FIND OBJECT STATE")
                            leftView = True
                            break

                        elif (offset_x < desiredOffsetMin - 100):
                            sendCommand("L_LEFT")
                            time.sleep(2)
                            print("Moving Left")

                        elif (desiredOffsetMax + 100 < offset_x ):
                            sendCommand("L_RIGHT")
                            time.sleep(2)
                            print("Moving Right")

                        elif (offset_x < desiredOffsetMin - 20):
                            sendCommand("M_LEFT")
                            time.sleep(2)
                            print("Moving Left")

                        elif (desiredOffsetMax + 20 < offset_x):
                            sendCommand("M_RIGHT")
                            time.sleep(2)
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

                    if (leftView == True): currentState = state.FIND_USER
                    else: 

                        time.sleep(3)
                        
                        currentState = state.TAKE_INSTRUCTION

                case state.PICKUP_OBJ: # PICKUP will get objects around 24cm from front wheel
                    printCurrentState(currentState)

                    sendCommand("PICKUP")
                    time.sleep(30)

                    # sendCommand("TURN_AROUND")
                    # time.sleep(5)

                    currentState = state.FIND_USER

                case _:
                    print("Current State: UNKNOWN STATE")

    except KeyboardInterrupt:
        print("Running interuppted by User")
    finally:
        sendCommand("STOP")

        # Reset Servo Camera Pan and Tilt positions 
        sendCommand("SERVO PAN 0")
        time.sleep(3)
        sendCommand("SERVO TILT 90")
        time.sleep(3)
        sendCommand("SERVO PICK1 0")
        time.sleep(3)
        sendCommand("SERVO PICK2 180")
        time.sleep(3)

        print("ENDING...")


if __name__ == "__main__":
    main()
