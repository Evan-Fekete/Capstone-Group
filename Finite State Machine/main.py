import math
from enum import Enum

# Define Constants for States for FSM
class state(Enum):
    STARTUP = 1
    TAKE_INSTRUCTION = 2
    FIND_OBJ = 3
    TRAVEL_TO_OBJ = 4
    RETURN_OBJ = 5

def main():
    print("Starting Raspberry Pi FSM...")
    
    currentState = state.STARTUP

    # main match statement used for running code for current state
    while(1):
        match currentState:
            case state.STARTUP:
                print("Current State: STARTUP")
            case state.TAKE_INSTRUCTION:
                print("Current State: TAKE_INSTRUCTION")
            case state.FIND_OBJ:
                print("Current State: FIND_OBJ")
            case state.TRAVEL_TO_OBJ:
                print("Current State: TRAVEL_TO_OBJ")
            case state.RETURN_OBJ:
                print("Current State: RETURN_OBJ")
            case _:
                print("Current State: UNKNOWN STATE")

if __name__ == "__main__":
    main()