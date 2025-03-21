import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from docx import Document
import fitz  # PyMuPDF

# Load .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define folders
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
INSTRUCTIONS_FILE = Path("instructions.txt")
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

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
    if file_path.suffix == ".txt":
        return read_txt(file_path)
    elif file_path.suffix == ".docx":
        return read_docx(file_path)
    elif file_path.suffix == ".pdf":
        return read_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

# Load instructions from file if it exists
if INSTRUCTIONS_FILE.exists():
    instructions = read_txt(INSTRUCTIONS_FILE)
    print(f"🗒️  Loaded instructions from instructions.txt")
else:
    instructions = "Speak clearly, with a warm and narrative tone."
    print("ℹ️  No instructions.txt found. Using default instructions.")

# Get all input files
input_files = list(INPUT_DIR.glob("*"))
if not input_files:
    print("❌ No files found in the 'input' folder.")
    exit()

for file in input_files:
    try:
        print(f"🎤 Processing: {file.name}")
        text = read_input_file(file)

        # Skip empty or very short files
        if not text or len(text.strip()) < 10:
            print(f"⚠️ File is empty or too short: {file.name}")
            continue

        output_file = OUTPUT_DIR / (file.stem + ".mp3")

        # Using the recommended streaming approach instead of stream_to_file
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="ballad",
            input=text,
            instructions=instructions
        ) as response:
            # Save the streaming response to file
            bytes_written = 0
            with open(str(output_file), 'wb') as f:
                for chunk in response.iter_bytes():
                    bytes_written += len(chunk)
                    f.write(chunk)
            
            print(f"✅ Audio saved to: {output_file} ({bytes_written} bytes)")

    except Exception as e:
        print(f"❌ Error with file {file.name}: {e}")