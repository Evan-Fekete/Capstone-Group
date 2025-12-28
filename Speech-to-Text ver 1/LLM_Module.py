import ollama

def TextToJSON(prompt: str, model_name = "gemma3:1b") -> str:

    # Example User Input for testing
    text = "Bring me my red cup"

    prompt = f'''{{
        "system": "You are a robot control agent. Convert user instructions into JSON. Only output the JSON output nothing else",
            "schema": {{
                "action": "fetch|place|deliver|stop",
                "object": {{
                    "name": "string",
                    "color": "string or null",
                    "size": "string or null"
                }},
                "location": {{
                    "from": "string or null"
                }},
                "to": "string or null"
            }}
        }} User: """{text}"""'''

    

    response = ollama.chat(model=model_name, messages=[
        {"role": "user", "content": prompt}
    ])

    # Return the model's response
    reply = response['message']['content']
    return reply