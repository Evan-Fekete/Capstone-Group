# When running on Pi input command for virtual environment packages:

# source ~/my_env/bin/activate

import numpy as np
from LLM_Module import TextToJSON

def main():
    print("LLM Testing...\n")

    formatted = " "

    reply = TextToJSON(formatted)

    print("\nLLM Response:\n", reply)

if __name__ == "__main__":
    main()