# Universal Text-to-Speech (TTS) Script

![Python](https://img.shields.io/badge/python-3.12-blue) ![OpenAI API](https://img.shields.io/badge/OpenAI-TTS-orange) ![License: MIT](https://img.shields.io/badge/license-MIT-green)

This project converts text files into lifelike speech audio using OpenAI's text-to-speech API.
It supports `.txt`, `.docx`, and `.pdf` input files and generates `.mp3` audio files.

---

## 🔧 Setup

### 1. Clone this repository or copy the files

### 2. Create and activate a virtual environment (Windows)
```bash
python -m venv tts-venv
.\tts-venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install openai python-dotenv python-docx pymupdf
```

### 4. Add your OpenAI API key
Create a `.env` file in the root directory with the following content:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Add input files
Place your `.txt`, `.docx`, or `.pdf` files inside the `input/` folder.

### 6. (Optional) Add voice instructions
Create a file named `instructions.txt` with the desired style, e.g.:
```
Speak like a calm narrator with a British accent and a slightly poetic rhythm.
```
If this file is missing, a default narration style will be used.

### 7. (Alternative) Use the simple script `tts-generate.py`
You can also use the simpler version `tts-generate.py`, which allows you to:
- Manually paste your text and instructions inside the script itself
- Use it for quick tests or single prompts without file handling

To run it:
```bash
python tts-generate.py
```
Edit the text and instruction fields directly in the file.

---

## ▶️ How to Run

### Activate the virtual environment (Windows):
```bash
.\tts-venv\Scripts\activate
```

### Run the universal script
```bash
python universal_tts.py
```
All files in the `input/` folder will be processed automatically.

---

## 💬 Supported TTS Models

For intelligent realtime applications, use the `gpt-4o-mini-tts` model — OpenAI’s newest and most flexible TTS engine.
You can customize the voice using the `instructions` parameter:

### You can control:
- Accent
- Emotional range
- Intonation
- Impressions
- Speed of speech
- Tone
- Whispering

Other available models:
- `tts-1` (faster, lower quality)
- `tts-1-hd` (high quality, higher latency)

---

## 🗣️ Voice Options
Choose from 11 built-in voices:
- alloy
- ash
- ballad
- coral
- echo
- fable
- onyx
- nova *(default in this script)*
- sage
- shimmer

You can preview them at [openai.fm](https://openai.fm)

---

## 📂 Output
All generated audio files will be saved in the `output/` folder with the same name as the input file.

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Enjoy building your custom voice assistant or narrator! 🎧

