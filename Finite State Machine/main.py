# Before working start VENV also input: "git pull origin main"
# 
# Also if you want to connect to Virtual Environment
# Enter: source /FSMvenv/bin/activate
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
    print("Current State: " + currentState)

def sendCommand(cmd):
    ser.write(f'{cmd}\n'.encode())
    time.sleep(0.1)
    # read back a confirmation 
    if ser.in_waiting:
        return ser.readline().decode().strip()
    return None

def save_json_response(response_str, filename="Object.json"):
    """Save LLM JSON response to a file in the script directory."""
    filepath = os.path.join(SCRIPT_DIR, filename)
    try:
        # Parse the JSON string to validate it
        json_data = json.loads(response_str)
        # Write to file with pretty formatting
        with open(filepath, 'w') as f:
            json.dump(json_data, f, indent=4)
        print(f"JSON saved to: {filepath}")
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        # Save raw response anyway for debugging
        with open(filepath, 'w') as f:
            f.write(response_str)
        return None

def main():
    print("Starting Raspberry Pi FSM...")
    
    try:
        currentState = state.STARTUP
        # main match statement used for running code for current state
        while(1):
            match currentState:
                case state.STARTUP:
                    printCurrentState(currentState)                    
                    time.sleep(5)
                    currentState = state.TAKE_INSTRUCTION
                case state.TAKE_INSTRUCTION:
                    print("Current State: TAKE_INSTRUCTION")
                    # # Uncomment to activate recording and transcription
                    # audio = speech.record_audio()
                    # user_input = speech.transcribe_audio(audio)
                    # Uncomment to define user input
                    user_input = "Bring me the apple"
                    # JSON Schema prompt used to return JSON schema for vision system
                    prompt = """You are a robot control agent. Convert user instructions found Real User Input. If parameter is not known then output unknown always display action, object, and color.
                        Schema: action (fetch/place/deliver/stop), object (apple/mug/bottle/shoe), color (red/blue/green/white/unknown)
                        Example:
                        User: bring me the red apple
                        JSON: {{"action":"fetch","object":"apple","color":"red"}}
                        Real User Input:
                        User: {text}
                        JSON:"""
                    formatted = prompt.format(text = user_input)
                    reply = speech.TextToJSON(formatted)
                    print("\nLLM Response:\n", reply)
                    
                    # Save the JSON response to file
                    json_data = save_json_response(reply)
                    
                    currentState = state.FIND_OBJ
                    time.sleep(5)
                    
                case state.FIND_OBJ:
                    print("Current State: FIND_OBJ")

                    iter = 0
                    
                    # TODO: create loop for looking for object and when found go to travel state
                    while(1):
                        if (iter == 0):
                            sendCommand("SWIVELLEFT")
                        else:
                            sendCommand("SWIVELRIGHT")

                        [findObject, foundBool, bounding_x, bounding_y] = vision.look_around()

                        if (foundBool == True):
                            print(findObject + " has been found.")
                            servoPosition = sendCommand("SWIVELSTOP")
                            print("Servo is at " + servoPosition)
                            break
                    
                case state.TRAVEL_TO_OBJ:
                    print("Current State: TRAVEL_TO_OBJ")
                    # TODO: Add logic for moving towards object and checking if object is in view if not go back state
                case state.FIND_USER:
                    print("Current State: FIND_USER")
                
                case state.RETURN_OBJ:
                    print("Current State: RETURN_OBJ")

                case state.PICKUP_OBJ:
                    print("Current State: PICKUP_OBJ")

                case _:
                    print("Current State: UNKNOWN STATE")

    except KeyboardInterrupt:
        print("Running interuppted by User")
    finally:
        print("ENDING...")
    
if __name__ == "__main__":
    main()