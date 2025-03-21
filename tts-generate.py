from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ✅ Use new-style client init (IMPORTANT)
client = OpenAI(api_key=api_key)

# Output file path
speech_file_path = Path("alberto_voice_output.mp3")

# Create the speech with instruction control
response = client.audio.speech.create(
    model="gpt-4o-mini-tts",  # ✅ New TTS model
    voice="coral",  # or shimmer, alloy, etc.
    input=(
        "Welcome back, Alberto. The system is ready for your command. "
        "In a world where machines learn to speak like humans, one voice rises above the rest — "
        "calm, confident, and ready to guide you through a future shaped by innovation and imagination. "
        "Welcome to the age of intelligent conversation. Here, your words are not just heard, they are understood. "
        "Ideas become actions, and curiosity is no longer limited by silence. "
        "This is not just the next chapter in technology — it’s the beginning of a new dialogue between humans and machines."
    ),
    instructions="Sound like a futuristic assistant with calm confidence and a hint of wonder.",
)

# Save to file
response.stream_to_file(speech_file_path)
print("✅ Done! Audio saved to:", speech_file_path)
