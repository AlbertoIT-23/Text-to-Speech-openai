# Universal Text-to-Speech (TTS) App

![Python](https://img.shields.io/badge/python-3.12-blue) ![OpenAI API](https://img.shields.io/badge/OpenAI-TTS-orange) ![License: MIT](https://img.shields.io/badge/license-MIT-green)

This project converts text and documents into lifelike speech using OpenAI's text-to-speech API.
Featuring an intuitive graphical interface, the app supports multiple document formats, voices, and customization options.

![GUI Screenshot](https://github.com/user-attachments/assets/c8159f4b-f437-4aa6-8425-3b9326db5a24)

## 🎬 Video Demo

Watch the application in action: [YouTube Demo](https://youtu.be/O9F0fX2OusA)

## ✨ Key Features

- **User-friendly GUI** with scrollable interface
- **Multiple input options** - direct text entry or file import
- **Multi-format support** - process `.txt`, `.docx`, and `.pdf` files
- **11 voice options** including special enhanced voices
- **Customizable voice instructions** for tone, emotion, and style
- **Audio preview** before generating full files
- **Multiple output formats** - mp3, opus, aac, flac, wav, pcm
- **Secure API key storage** options (system keyring or .env file)
- **API key management** - store, update, and delete API keys securely
- **Custom output directory** selection

## 💿 Quick Start - Windows Installer

The easiest way to get started is with our Windows installer:

1. **Download**: Get the latest installer from the [Releases](https://github.com/AlbertoIT-23/Text-to-Speech-openai/releases) page
2. **Install**: Run the installer and follow the prompts
3. **Launch**: Start Universal-TTS from your Start menu or desktop shortcut
4. **Configure**: Enter your OpenAI API key when prompted on first launch

### ⚠️ Antivirus Notice

Some antivirus programs may flag the installer as suspicious. This is a common false positive that occurs with Python applications packaged as executables.

**Why this happens**: Tools like PyInstaller package Python code in a way that can trigger heuristic detection in some security software, even though the application is completely safe.

**What to do if this happens**:
1. If your antivirus quarantines the file, you can restore it from quarantine
2. Add an exception for the Universal-TTS application in your antivirus software
3. You can verify the installer's safety through our [VirusTotal scan](https://www.virustotal.com/gui/file/1a09d1fbadbdafb6ed9ac52f8c0357cb774adb8a6d67a1bf5e09248bd71081d1/behavior)
4. The application is open-source and contains no malicious code - you can review all source code in this repository

## 🔧 Developer Setup - From Source Code

If you prefer to run from source code or want to contribute to development:

### 1. Clone this repository or download the files

### 2. Create and activate a virtual environment (Windows)
```bash
python -m venv tts-venv
.\tts-venv\Scripts\activate
```

### 3. Install dependencies

This project was developed with Python 3.12.6. Install all required dependencies:

```bash
pip install openai==1.68.2 python-dotenv==1.0.1 python-docx==1.1.2 PyMuPDF==1.25.4 sounddevice==0.5.1 keyring==25.6.0
```

Or use the requirements.txt file:

```bash
pip install -r requirements.txt
```

#### Key Dependencies:
- **openai**: OpenAI API client for text-to-speech
- **python-dotenv**: For loading API keys from .env files
- **python-docx**: For reading .docx files
- **PyMuPDF**: For reading PDF files
- **sounddevice**: For audio preview functionality
- **keyring**: For secure API key storage (recommended)
- **tkinter**: For the GUI (included in Python standard library)

> **Note for Linux users**: You might need to install tkinter separately.

### 4. Launch the GUI application
```bash
python universal-tts-gui.py
```

## ▶️ Using the Application

Regardless of installation method, you'll need to configure your OpenAI API key on first launch:

### 1. Configure your OpenAI API key
- Click the "⚙️ Config API Key" button
- Enter your API key
- Choose a storage method:
  - **System credential manager** (recommended for security)
  - **.env file** (convenient but less secure)
  - **Session only** (temporary use)
  - You can also **delete your stored API key** from all locations if needed

### 2. Text Input Options
- **Text Input tab**: Directly type or paste text
- **File Input tab**: Import content from TXT, DOCX, or PDF files

### 3. Voice Configuration
- **Voice**: Choose from 11 different voices
  - Regular voices: alloy, echo, fable, onyx, nova, shimmer
  - Special voices (marked with *): ash, ballad, coral, sage, verse
- **Model**: Select the TTS model
  - **gpt-4o-mini-tts**: Most flexible, supports all voices and instructions
  - **tts-1**: Faster, supports limited voice set
  - **tts-1-hd**: Highest quality, supports limited voice set
- **Format**: Choose output audio format (mp3, opus, aac, flac, wav, pcm)
- **Speed**: Adjust speech speed (0.25x to 4.0x, works with tts-1 and tts-1-hd only)
- **Voice instructions**: Customize speaking style, tone, accent, etc.

### 4. Output Options
- Select or create custom output folder
- Files are saved with descriptive names including voice and timestamp

### 5. Controls
- **Preview Audio**: Test a short sample before generating the full file
- **Generate Audio File**: Process the entire text and save to disk

## 🔑 API Key Management

The app provides comprehensive API key management:

- **Multiple storage options**:
  - System credential manager (most secure, requires keyring package)
  - .env file (convenient but less secure)
  - Session only (temporary use)
- **Key visibility toggle**: Optionally show/hide your key while typing
- **Delete functionality**: Remove your API key from all storage locations
  - System credential manager
  - .env file
  - Current session
- **Automatic detection**: The app checks all possible storage locations on startup

## 🗣️ Voice Customization

The app supports OpenAI's voice customization through instructions. You can control:

- **Accent**: British, American, Australian, etc.
- **Emotion**: Happy, sad, excited, calm, etc.
- **Speaking style**: Narrative, conversational, formal, etc.
- **Pace and rhythm**: Speed variations, pauses, emphasis
- **Character impressions**: Specific personas or styles

Example instruction:
```
Speak clearly with a warm British accent, use a contemplative pace, and add subtle emotion when appropriate.
```

## 🔄 Alternative Script Options

If you prefer command-line usage or need automation options, two alternative scripts are included:

### 1. Universal Script (universal_tts.py)
A batch processing script that automatically converts all files in the `input/` folder:

```bash
python universal_tts.py
```

- Place files in the `input/` directory and they'll be processed automatically
- Creates an `output/` folder with the generated audio files
- Uses voice instructions from `instructions.txt` if available
- Great for batch processing multiple documents without GUI interaction
- Preserves original filenames with added voice information

### 2. Simple Script (tts-generate.py)
A minimal script for quick generation of speech from text strings:

```bash
python tts-generate.py
```

- Edit the script directly to input your text and instructions
- Useful for quick tests, demonstrations, or simple prompts
- No file handling or GUI overhead
- Perfect for integration into other scripts or workflows
- Ideal for developers wanting to understand the basic API implementation

## 🔄 Open Source & Extensible
This project is fully open source and designed to be extended. Feel free to fork it, improve it, or use it as a foundation for your own TTS applications. Pull requests welcome!
Some ideas for extensions:

- Add batch processing capabilities
- ~~Add option to delete/remove stored API keys~~ ✅ Implemented!
- Create language detection and automatic voice selection
- Implement text chunking for longer documents
- Add a progress indicator for long audio generation
- Build a web-based version

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Enjoy creating realistic voiced content with the Universal TTS App! 🎧