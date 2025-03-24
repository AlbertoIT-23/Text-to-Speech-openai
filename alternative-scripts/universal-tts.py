import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from docx import Document
import fitz  # PyMuPDF
import time
import datetime

# ========== CONFIGURATION OPTIONS ============
# You can modify these values to change the output
VOICE = "coral"        # Options: alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse
MODEL = "gpt-4o-mini-tts"  # Options: gpt-4o-mini-tts, tts-1, tts-1-hd
FORMAT = "mp3"         # Options: mp3, opus, aac, flac, wav, pcm
SPEED = 1.0            # Range: 0.25 to 4.0
# ============================================

# Load .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define script directory and folders relative to the script
SCRIPT_DIR = Path(__file__).parent.absolute()
INPUT_DIR = SCRIPT_DIR / "input"
OUTPUT_DIR = SCRIPT_DIR / "output"
INSTRUCTIONS_FILE = SCRIPT_DIR / "instructions.txt"

# Create input and output directories if they don't exist
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"🔍 Script directory: {SCRIPT_DIR}")
print(f"📁 Input directory: {INPUT_DIR}")
print(f"📁 Output directory: {OUTPUT_DIR}")
print(f"📄 Looking for instructions at: {INSTRUCTIONS_FILE}")

# Read .txt files
def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

# Read .docx files
def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

# Read .pdf files
def read_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join([page.get_text() for page in doc])

# Select reader based on file extension
def read_input_file(file_path):
    if file_path.suffix.lower() == ".txt":
        return read_txt(file_path)
    elif file_path.suffix.lower() == ".docx":
        return read_docx(file_path)
    elif file_path.suffix.lower() == ".pdf":
        return read_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

# Validate speed parameter
if SPEED < 0.25 or SPEED > 4.0:
    print(f"⚠️ Warning: Speed value {SPEED} is out of range (0.25-4.0). Using default 1.0.")
    SPEED = 1.0

# Load instructions from file if it exists
if INSTRUCTIONS_FILE.exists():
    instructions = read_txt(INSTRUCTIONS_FILE)
    print(f"🗒️ Loaded instructions from: {INSTRUCTIONS_FILE}")
else:
    instructions = "Speak clearly, with a warm and narrative tone."
    print(f"ℹ️ No instructions file found at: {INSTRUCTIONS_FILE}")
    print(f"📝 Using default instructions: \"{instructions}\"")

# Print configuration details
print(f"🎤 Voice: {VOICE}")
print(f"🎛️ Model: {MODEL}")
print(f"🎵 Format: {FORMAT}")
print(f"⏩ Speed: {SPEED}")

# Get all input files
input_files = list(INPUT_DIR.glob("*"))
if not input_files:
    print(f"❌ No files found in the input folder: {INPUT_DIR}")
    exit()

# Get the start time for the script execution
script_start_time = time.time()
print(f"🚀 Starting batch processing at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📂 Found {len(input_files)} files to process")

for i, file in enumerate(input_files, 1):
    try:
        start_time = time.time()  # Track time for individual file processing
        print(f"\n[{i}/{len(input_files)}] 🔊 Processing: {file.name}")
        text = read_input_file(file)

        # Skip empty or very short files
        if not text or len(text.strip()) < 10:
            print(f"⚠️ File is empty or too short: {file.name}")
            continue
        
        # Check if text exceeds the API character limit
        MAX_CHARS = 8192
        if len(text) > MAX_CHARS:
            print(f"⚠️ Text in {file.name} exceeds the {MAX_CHARS} character limit ({len(text)} chars). Truncating...")
            text = text[:MAX_CHARS]
        else:
            print(f"📝 Text length: {len(text)} characters")
        
        # Generate timestamp for the filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"{file.stem}_{timestamp}.{FORMAT}"

        print(f"⏳ Generating audio...")
        
        # Using the recommended streaming approach
        with client.audio.speech.with_streaming_response.create(
            model=MODEL,
            voice=VOICE,
            input=text,
            instructions=instructions,
            response_format=FORMAT,
            speed=SPEED
        ) as response:
            # Save the streaming response to file
            bytes_written = 0
            with open(str(output_file), 'wb') as f:
                for chunk in response.iter_bytes():
                    bytes_written += len(chunk)
                    f.write(chunk)
            
            # Calculate processing time
            duration = time.time() - start_time
            file_size_kb = bytes_written / 1024
            print(f"✅ Audio saved to: {output_file}")
            print(f"📊 File size: {file_size_kb:.2f} KB")
            print(f"⏱️ Processing time: {duration:.2f} seconds")

    except Exception as e:
        print(f"❌ Error with file {file.name}: {e}")

# Print summary
total_duration = time.time() - script_start_time
files_processed = len(input_files)
print(f"\n✨ Batch processing completed in {total_duration:.2f} seconds")
print(f"📊 Processed {files_processed} files")
print(f"📂 Output files saved to: {OUTPUT_DIR.absolute()}")

# Calculate and print average processing time if any files were processed
if files_processed > 0:
    avg_time = total_duration / files_processed
    print(f"⏱️ Average processing time per file: {avg_time:.2f} seconds")