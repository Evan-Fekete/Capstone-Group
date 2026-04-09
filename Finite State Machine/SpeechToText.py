import whisper
import sounddevice as sd
import numpy as np
from LLM_Module import promptLLM

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
    # print("Speech to Text Program Starting...\n")
    # audio = record_audio()
    # user_input = transcribe_audio(audio)

    user_input = "Bring me the red cup"

    # Define your prompt here
    prompt = """You are a robot control agent. Convert user instructions into JSON.

    Schema: action (fetch/place/deliver/stop), object (apple/mug/bottle/shoe), color (red/blue/green/white), to (location or null)

    Example:
    User: bring me the red apple
    JSON: {{"action":"fetch","object":"apple","color":"red","to":null}}

    User: {text}
    JSON:"""

    formatted = prompt.format(text = user_input)

    reply = TextToJSON(formatted)

    print("\nLLM Response:\n", reply)