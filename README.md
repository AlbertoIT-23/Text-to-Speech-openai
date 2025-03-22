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

This project was developed with Python 3.12.6. You can install all required dependencies using:

```bash
pip install openai==1.68.2 python-dotenv==1.0.1 python-docx==1.1.2 PyMuPDF==1.25.4 sounddevice==0.5.1 keyring==25.6.0
```

Or create a `requirements.txt` file with these dependencies and run:

```bash
pip install -r requirements.txt
```

The application uses the following main libraries:
- openai: OpenAI API client for text-to-speech
- python-dotenv: For loading API keys from .env files
- python-docx: For reading .docx files
- PyMuPDF: For reading PDF files
- sounddevice: For audio preview functionality
- keyring: For secure API key storage (optional)

Note: The GUI uses tkinter which is included in the Python standard library. On some Linux distributions, you might need to install it separately.

### 4. Add your OpenAI API key
Create a `.env` file in the root directory with the following content:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Create the `input/` folder  
If it doesn't exist, manually create a folder named `input/` in the root directory.  
Then place your `.txt`, `.docx`, or `.pdf` files inside it.

### 6. Add voice instructions
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

### Or use the GUI version
```bash
python universal-tts-gui.py
```
The graphical interface allows you to:
- Input text directly or load files
- Select from 11 different voices
- Choose the TTS model
- Customize voice instructions
- Preview audio before generating the full file
- Easily manage your API key
- Select output folder

![image](https://github.com/user-attachments/assets/6df3632f-f938-43e2-8f53-65bca0727217)

---

## 💬 Supported TTS Models

For intelligent realtime applications, use the `gpt-4o-mini-tts` model — OpenAI's newest and most flexible TTS engine.
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
- nova
- sage
- shimmer
- verse

You can preview them at [openai.fm](https://openai.fm)

---

## 📂 Output
All generated audio files will be saved in the `output/` folder with the same name as the input file.

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Enjoy building your custom voice assistant or narrator! 🎧
