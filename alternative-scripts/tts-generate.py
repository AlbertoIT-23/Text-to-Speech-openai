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

# ========== CONFIGURATION OPTIONS ============
# You can modify these values to change the output
VOICE = "coral"        # Options: alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse
MODEL = "gpt-4o-mini-tts"  # Options: gpt-4o-mini-tts, tts-1, tts-1-hd
FORMAT = "mp3"         # Options: mp3, opus, aac, flac, wav, pcm
SPEED = 1.0            # Range: 0.25 to 4.0
# ============================================

# Output file path in the output directory
timestamp = time.strftime("%Y%m%d_%H%M%S")
speech_file_path = output_dir / f"speech_{timestamp}.{FORMAT}"

input_text = """Welcome to the Universal Text-to-Speech tool. This is a simple example of what you can create with OpenAI's speech synthesis API. You can customize the voice, tone, and style to suit your needs."""
instructions = """Voice: High-energy, upbeat, and encouraging, projecting enthusiasm and motivation.\n\nPunctuation: Short, punchy sentences with strategic pauses to maintain excitement and clarity.\n\nDelivery: Fast-paced and dynamic, with rising intonation to build momentum and keep engagement high.\n\nPhrasing: Action-oriented and direct, using motivational cues to push participants forward.\n\nTone: Positive, energetic, and empowering, creating an atmosphere of encouragement and achievement."""

# Check the character limit
MAX_CHARS = 8192
if len(input_text) > MAX_CHARS:
    print(f"⚠️ Warning: Input text exceeds the {MAX_CHARS} character limit ({len(input_text)} chars)")
    print(f"⚠️ Text will be truncated to {MAX_CHARS} characters")
    input_text = input_text[:MAX_CHARS]

# Validate speed parameter
if SPEED < 0.25 or SPEED > 4.0:
    print(f"⚠️ Warning: Speed value {SPEED} is out of range (0.25-4.0). Using default 1.0.")
    SPEED = 1.0

print(f"🔊 Generating audio with voice: {VOICE}")
print(f"🎛️ Using model: {MODEL}")
print(f"🎚️ Speed: {SPEED}")
print(f"🎵 Format: {FORMAT}")
print(f"📝 Input text length: {len(input_text)} characters")
print(f"⏳ Please wait...")

start_time = time.time()

try:
    # Create the speech with instruction control
    with client.audio.speech.with_streaming_response.create(
        model=MODEL,
        voice=VOICE,
        input=input_text,
        instructions=instructions,
        response_format=FORMAT,
        speed=SPEED
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
        
except Exception as e:
    print(f"❌ Error generating speech: {e}")
    sys.exit(1)