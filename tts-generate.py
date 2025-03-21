from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ✅ Use new-style client init (IMPORTANT)
client = OpenAI(api_key=api_key)

# Ensure output directory exists
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# Output file path in the output directory
speech_file_path = output_dir / "output.mp3"

input = """Welcome to the Universal Text-to-Speech tool. This is a simple example of what you can create with OpenAI's speech synthesis API. You can customize the voice, tone, and style to suit your needs."""
instructions = """Voice: High-energy, upbeat, and encouraging, projecting enthusiasm and motivation.\n\nPunctuation: Short, punchy sentences with strategic pauses to maintain excitement and clarity.\n\nDelivery: Fast-paced and dynamic, with rising intonation to build momentum and keep engagement high.\n\nPhrasing: Action-oriented and direct, using motivational cues to push participants forward.\n\nTone: Positive, energetic, and empowering, creating an atmosphere of encouragement and achievement."""

# Create the speech with instruction control
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",  # ✅ New TTS model
    voice="coral",  # or shimmer, alloy, etc.
    input=input,
    instructions=instructions,
) as response:
    # Save the streaming response to file
    with open(str(speech_file_path), 'wb') as f:
        for chunk in response.iter_bytes():
            f.write(chunk)

print("✅ Done! Audio saved to:", speech_file_path)