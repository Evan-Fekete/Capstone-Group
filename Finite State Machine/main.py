# Before working start VENV also input: "git pull origin main"
# 
# IF ON WINDOWS
# Enter: source /FSMvenv/bin/activate
#
# IF ON PI
# Enter: FSMvenv/bin/activate 

import math
import time
import navigation as nav
import SpeechToText as speech
from enum import Enum

# Define Constants for States for FSM
class state(Enum):
    STARTUP = 1
    TAKE_INSTRUCTION = 2
    FIND_OBJ = 3
    TRAVEL_TO_OBJ = 4
    FIND_USER = 5
    RETURN_OBJ = 6

def main():
    print("Starting Raspberry Pi FSM...")
    
    try:
        currentState = state.STARTUP

        # main match statement used for running code for current state
        while(1):
            match currentState:
                case state.STARTUP:
                    print("Current State: STARTUP")

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
                    prompt = """You are a robot control agent. Convert user instructions into JSON.

                    Schema: action (fetch/place/deliver/stop), object (apple/mug/bottle/shoe), color (red/blue/green/white), to (location or null)

                    Example:
                    User: bring me the red apple
                    JSON: {{"action":"fetch","object":"apple","color":"red","to":null}}

                    User: {text}
                    JSON:"""

                    formatted = prompt.format(text = user_input)

                    reply = speech.TextToJSON(formatted)

                    print("\nLLM Response:\n", reply)

                    currentState = state.FIND_OBJ
                    time.sleep(5)
                    
                case state.FIND_OBJ:
                    print("Current State: FIND_OBJ")

                    # TODO: Add Logic for identifying object and then going into TRAVEL_TO_OBJ STATE

                    time.sleep(5)

                case state.TRAVEL_TO_OBJ:
                    print("Current State: TRAVEL_TO_OBJ")
                    reactive_step()

                    # TODO: Add logic for moving towards object and checking if object is in view if not go back state

                case state.RETURN_OBJ:
                    print("Current State: RETURN_OBJ")
                case _:
                    print("Current State: UNKNOWN STATE")

    except KeyboardInterrupt:
        print("Running interuppted by User")
    finally:
        print("ENDING...")
        # nav.cleanup()

    

if __name__ == "__main__":
    main()