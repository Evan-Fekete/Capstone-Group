# When running on Pi input command for virtual environment packages:

# source ~/my_env/bin/activate

import ollama

def TextToJSON(speech_input: str, model_name = "gemma3:270m") -> str:

    # # Example User Input for testing
    # speech_input = "my name is john bring me the red mug"

    # schema = """You are a robot control agent. Convert user instructions into JSON.

    # Schema: name (john, steve, bob), action (fetch), object (apple/mug/bottle/shoe), color (red/blue/green/white), to (location or null)

    # Example:
    # User: my name is john bring me the red apple
    # JSON: {{"name":"john", "action":"fetch","object":"apple","color":"red","to":null}}

    # User: {text}
    # JSON:"""

    # prompt = schema.format(text = speech_input)

    prompt = speech_input

    response = ollama.chat(model=model_name, messages=[
        {"role": "user", "content": prompt}
    ])

    # Return the model's response
    reply = response['message']['content']
    return reply