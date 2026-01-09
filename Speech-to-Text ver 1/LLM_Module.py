import ollama

def TextToJSON(speech_input: str, model_name = "gemma3:270m") -> str:

    # Example User Input for testing
    speech_input = "get the blue mug from the kitchen"

    prompt = """You are a robot control agent. Convert user instructions into JSON.

    Schema: action (fetch/place/deliver/stop), object (apple/mug/bottle/shoe), color (red/blue/green/white), to (location or null)

    Example:
    User: bring me the red apple
    JSON: {{"action":"fetch","object":"apple","color":"red","to":null}}

    User: {text}
    JSON:"""

    formatted = prompt.format(text = speech_input)

    response = ollama.chat(model=model_name, messages=[
        {"role": "user", "content": formatted}
    ])

    # Return the model's response
    reply = response['message']['content']
    return reply