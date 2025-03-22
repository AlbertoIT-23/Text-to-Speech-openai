from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
import sys
import time

# Load .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Error: No API key found. Please set OPENAI_API_KEY in your .env file or environment variables.")
    sys.exit(1)

# ✅ Use new-style client init (IMPORTANT)
client = OpenAI(api_key=api_key)

# Ensure output directory exists
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# Output file path in the output directory
timestamp = time.strftime("%Y%m%d_%H%M%S")
speech_file_path = output_dir / f"speech_{timestamp}.mp3"

input_text = """Welcome to the Universal Text-to-Speech tool. This is a simple example of what you can create with OpenAI's speech synthesis API. You can customize the voice, tone, and style to suit your needs."""
instructions = """Voice: High-energy, upbeat, and encouraging, projecting enthusiasm and motivation.\n\nPunctuation: Short, punchy sentences with strategic pauses to maintain excitement and clarity.\n\nDelivery: Fast-paced and dynamic, with rising intonation to build momentum and keep engagement high.\n\nPhrasing: Action-oriented and direct, using motivational cues to push participants forward.\n\nTone: Positive, energetic, and empowering, creating an atmosphere of encouragement and achievement."""

# Check the character limit
MAX_CHARS = 4096
if len(input_text) > MAX_CHARS:
    print(f"⚠️ Warning: Input text exceeds the {MAX_CHARS} character limit ({len(input_text)} chars)")
    print(f"⚠️ Text will be truncated to {MAX_CHARS} characters")
    input_text = input_text[:MAX_CHARS]

print(f"🔊 Generating audio with voice: coral")
print(f"📝 Input text length: {len(input_text)} characters")
print(f"⏳ Please wait...")

start_time = time.time()

# Create the speech with instruction control
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",  # ✅ New TTS model
    voice="coral",  # or shimmer, alloy, etc.
    input=input_text,
    instructions=instructions,
) as response:
    # Save the streaming response to file
    bytes_written = 0
    with open(str(speech_file_path), 'wb') as f:
        for chunk in response.iter_bytes():
            bytes_written += len(chunk)
            f.write(chunk)
    
    duration = time.time() - start_time
    print(f"✅ Done! Audio saved to: {speech_file_path}")
    print(f"📊 Statistics:")
    print(f"   - Audio file size: {bytes_written / 1024:.2f} KB")
    print(f"   - Processing time: {duration:.2f} seconds")