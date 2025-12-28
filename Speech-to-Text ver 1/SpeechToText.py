import whisper
import sounddevice as sd
import numpy as np
from LLM_Module import TextToJSON

# Load Whisper model (use "tiny", "base", "small", etc. for faster results)
model = whisper.load_model("base")

SAMPLE_RATE = 16000  # Whisper expects 16 kHz audio
CHUNK_DURATION = 5    # seconds per audio chunk

def record_audio(duration=CHUNK_DURATION, samplerate=SAMPLE_RATE):
    print(f"\nListening for {duration} seconds...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    return np.squeeze(audio)

def transcribe_audio(audio):
    print("\nTranscribing...")
    result = model.transcribe(audio, fp16=False)
    text = result["text"].strip()
    print("You said:", text)
    return text

def main():
    print("Speech to Text Program Starting...\n")
    audio = record_audio()
    text = transcribe_audio(audio)

    # Define your prompt here
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

    reply = TextToJSON(prompt)

    print("\nLLM Response:\n", reply)

if __name__ == "__main__":
    main()
