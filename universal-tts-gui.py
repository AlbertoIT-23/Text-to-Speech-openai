import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path
from openai import OpenAI, AsyncOpenAI
from openai.helpers import LocalAudioPlayer
from dotenv import load_dotenv
from docx import Document
import fitz  # PyMuPDF
import threading
import logging
import json
import datetime
import asyncio

# Aggiungiamo il supporto per il sistema di credenziali
try:
    import keyring
    import getpass
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    logging.warning("keyring package not available. Install with: pip install keyring")

# Load .env file
load_dotenv()

class UniversalTTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal TTS")
        self.root.geometry("900x800")  # Dimensione iniziale più grande
        self.root.minsize(800, 700)   
        
        # Modifica inizializzazione della API key per usare il keyring se disponibile
        self.api_key = self.get_api_key_from_sources()
        self.client = None
        self.async_client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.async_client = AsyncOpenAI(api_key=self.api_key)
        
        # Setup logging
        self.setup_logging()
        
        # Set style
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 11))
        self.style.configure('TLabel', font=('Arial', 11))
        
        # Stili migliorati per i bottoni
        self.style.configure('Preview.TButton', 
                            font=('Arial', 10))
        
        # Stile per il bottone di generazione - più visibile
        self.style.configure('Big.TButton', 
                            font=('Arial', 11, 'bold'))
        
        # Frame per contenere il bottone colorato personalizzato
        self.create_widgets()
        
    def setup_logging(self):
        """Setup logging to file"""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create a log file with timestamp in name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"tts_log_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            filename=str(log_file),
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        logging.info("Application started")
        logging.info(f"Python version: {os.sys.version}")
        
        # Add a console handler too
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Universal Text-to-Speech", font=('Arial', 14, 'bold'))
        title_label.pack(pady=5)
        
        # API Key frame
        api_frame = ttk.LabelFrame(main_frame, text="OpenAI API Key", padding="5")
        api_frame.pack(fill=tk.X, padx=5, pady=3)
        
        api_row = ttk.Frame(api_frame)
        api_row.pack(fill=tk.X)
        
        self.api_entry = ttk.Entry(api_row, show="*", width=50)
        if self.api_key:
            self.api_entry.insert(0, self.api_key)
        self.api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        api_button = ttk.Button(api_row, text="Update API Key", command=self.update_api_key)
        api_button.pack(side=tk.RIGHT)
        
        # Input method tabs
        self.tab_control = ttk.Notebook(main_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tab 1: Direct Text Input
        text_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(text_tab, text="Text Input")
        
        text_label = ttk.Label(text_tab, text="Enter or paste text:")
        text_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.text_input = scrolledtext.ScrolledText(text_tab, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 2: File Input
        file_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(file_tab, text="File Input")
        
        file_frame = ttk.Frame(file_tab)
        file_frame.pack(fill=tk.X, padx=5, pady=10)
        
        file_label = ttk.Label(file_frame, text="Select file (TXT, DOCX, PDF):")
        file_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_button.pack(side=tk.RIGHT)
        
        preview_frame = ttk.LabelFrame(file_tab, text="File Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.file_preview = scrolledtext.ScrolledText(preview_frame, height=8)
        self.file_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Voice options frame
        voice_frame = ttk.LabelFrame(main_frame, text="Voice Options", padding="10")
        voice_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Voice selection
        voice_label = ttk.Label(voice_frame, text="Voice:")
        voice_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.voice_var = tk.StringVar(value="ballad")
        voice_options = ["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse"]
        voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, values=voice_options, width=15, state="readonly")
        voice_dropdown.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Model selection
        model_label = ttk.Label(voice_frame, text="Model:")
        model_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        self.model_var = tk.StringVar(value="gpt-4o-mini-tts")
        model_options = ["gpt-4o-mini-tts", "tts-1", "tts-1-hd"]
        model_dropdown = ttk.Combobox(voice_frame, textvariable=self.model_var, values=model_options, width=15, state="readonly")
        model_dropdown.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Voice instructions - modify to span full width
        instructions_label = ttk.Label(voice_frame, text="Voice instructions:")
        instructions_label.grid(row=1, column=0, sticky=tk.NW, padx=5, pady=5)
        
        # Configure voice_frame columns to properly distribute space
        voice_frame.columnconfigure(0, weight=0)  # Label column doesn't need to expand
        voice_frame.columnconfigure(1, weight=1)  # This column should expand to fill space
        voice_frame.columnconfigure(2, weight=0)  # Model label column
        voice_frame.columnconfigure(3, weight=1)  # Model dropdown column
        
        # ScrolledText directly in the frame without intermediate container
        self.instructions_text = scrolledtext.ScrolledText(voice_frame, height=6, wrap=tk.WORD)
        self.instructions_text.grid(row=1, column=1, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.instructions_text.insert(tk.END, "Speak clearly, with a warm and narrative tone.")
        
        # Output options
        output_frame = ttk.LabelFrame(main_frame, text="Output Options", padding="10")
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        output_path_label = ttk.Label(output_frame, text="Output folder:")
        output_path_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.output_path_var = tk.StringVar(value=str(Path("output")))
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=40)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        output_browse = ttk.Button(output_frame, text="Browse", command=self.browse_output_folder)
        output_browse.pack(side=tk.LEFT, padx=(0, 5))
        
        # Preview frame - NEW
        preview_btn_frame = ttk.Frame(main_frame)
        preview_btn_frame.pack(fill=tk.X, padx=10, pady=2)
        
        # Contenitore centrale per il bottone di anteprima
        center_preview_frame = ttk.Frame(preview_btn_frame)
        center_preview_frame.pack(pady=2)  # Centrato orizzontalmente
        
        preview_button = tk.Button(
            center_preview_frame, 
            text="▶ Anteprima Audio",
            command=self.preview_audio,
            font=('Arial', 10),
            background='#1976D2',
            foreground='white',
            activebackground='#2196F3',
            activeforeground='white',
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=2
        )
        preview_button.pack(padx=5, pady=2)  # Non più fill=tk.X
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Generate button - bottone più compatto e centrato
        generate_button_frame = ttk.Frame(main_frame)
        generate_button_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Contenitore centrale per il bottone genera
        center_generate_frame = ttk.Frame(generate_button_frame)
        center_generate_frame.pack(pady=2)  # Centrato orizzontalmente
        
        generate_button = tk.Button(
            center_generate_frame,
            text="GENERA FILE AUDIO",
            command=self.generate_speech,
            font=('Arial', 11, 'bold'),
            background='#2E7D32',
            foreground='white',
            activebackground='#388E3C',
            activeforeground='white',
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,  # Padding orizzontale più ampio
            pady=5
        )
        generate_button.pack(padx=5, pady=2)  # Non più fill=tk.X
    
    def get_api_key_from_sources(self):
        """Prova diverse fonti per ottenere l'API key in ordine di sicurezza."""
        # 1. Prova prima con la variabile d'ambiente (più sicura)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logging.info("API key found in environment variable")
            return api_key
            
        # 2. Prova con il sistema di credenziali del sistema operativo (se disponibile)
        if KEYRING_AVAILABLE:
            try:
                api_key = keyring.get_password(SERVICE_NAME, USERNAME)
                if api_key:
                    logging.info("API key found in system credential manager")
                    return api_key
            except Exception as e:
                logging.warning(f"Error accessing system credentials: {e}")
        
        # 3. Fallback: prova con il file .env (meno sicuro)
        # load_dotenv() è già stato chiamato all'inizio, quindi non serve ripeterlo qui
        
        logging.info("No API key found in any secure storage")
        return None    

    def update_api_key(self):
        new_key = self.api_entry.get().strip()
        if new_key:
            # Aggiorna per la sessione corrente
            os.environ["OPENAI_API_KEY"] = new_key
            self.api_key = new_key
            self.client = OpenAI(api_key=self.api_key)
            self.async_client = AsyncOpenAI(api_key=self.api_key)
            logging.info("API Key updated for current session")
            
            # Versione semplificata con scelte esplicite
            if KEYRING_AVAILABLE:
                # Prima domanda: vuoi salvare la chiave per usi futuri?
                save_choice = messagebox.askyesno(
                    "Salvataggio API Key",
                    "API Key aggiornata per questa sessione.\n\n"
                    "Vuoi salvare la chiave per usi futuri?\n\n"
                    "• SÌ = Salva per usi futuri\n"
                    "• NO = Usa solo per questa sessione",
                    icon=messagebox.QUESTION
                )
                
                if save_choice:
                    # Seconda domanda: quale metodo di salvataggio preferisci?
                    secure_choice = messagebox.askyesno(
                        "Metodo di Salvataggio",
                        "Quale metodo di salvataggio preferisci?\n\n"
                        "• SÌ = Salva nel gestore credenziali di sistema (consigliato)\n"
                        "• NO = Salva in un file .env (meno sicuro)",
                        icon=messagebox.QUESTION
                    )
                    
                    if secure_choice:
                        # Salva nel gestore credenziali
                        try:
                            SERVICE_NAME = "OpenAI-TTS-App"
                            USERNAME = getpass.getuser()
                            keyring.set_password(SERVICE_NAME, USERNAME, new_key)
                            messagebox.showinfo("Successo", 
                                              "API Key salvata in modo sicuro nel gestore credenziali del sistema")
                        except Exception as e:
                            messagebox.showerror("Errore", 
                                               f"Impossibile salvare nel gestore credenziali: {e}")
                    else:
                        # Salva in .env
                        self._save_to_env_file(new_key)
                else:
                    # Solo sessione
                    messagebox.showinfo("Successo", 
                                      "API Key aggiornata solo per questa sessione")
            else:
                # Versione semplificata senza keyring
                if messagebox.askyesno(
                    "Salvataggio API Key",
                    "API Key aggiornata per questa sessione.\n\n"
                    "Vuoi salvare la chiave in un file .env per usi futuri?\n\n"
                    "• SÌ = Salva nel file .env\n"
                    "• NO = Usa solo per questa sessione\n\n"
                    "Per una maggiore sicurezza, considera l'installazione del pacchetto 'keyring':\n"
                    "pip install keyring",
                    icon=messagebox.QUESTION
                ):
                    self._save_to_env_file(new_key)
                else:
                    messagebox.showinfo("Successo", 
                                      "API Key aggiornata solo per questa sessione")
            
            return True
        else:
            messagebox.showerror("Errore", "Inserisci una API Key valida")
            return False
    
    def _save_to_env_file(self, new_key):
        """Helper method to save API key to .env file with proper permissions"""
        try:
            env_path = Path(".env")
            
            # If .env exists, read and update it
            if env_path.exists():
                with open(env_path, "r") as f:
                    lines = f.readlines()
                
                found = False
                for i, line in enumerate(lines):
                    if line.startswith("OPENAI_API_KEY="):
                        lines[i] = f"OPENAI_API_KEY={new_key}\n"
                        found = True
                        break
                
                if not found:
                    lines.append(f"OPENAI_API_KEY={new_key}\n")
                
                with open(env_path, "w") as f:
                    f.writelines(lines)
            else:
                # Create new .env file
                with open(env_path, "w") as f:
                    f.write(f"OPENAI_API_KEY={new_key}\n")
            
            # Tentare di rendere il file accessibile solo all'utente corrente
            try:
                if os.name == 'nt':  # Windows
                    import subprocess
                    subprocess.call(['icacls', str(env_path), '/inheritance:r', '/grant', f'{os.getlogin()}:F'])
                else:  # Unix-like
                    os.chmod(str(env_path), 0o600)  # Read/write permissions for owner only
                logging.info("Applied restricted permissions to .env file")
            except Exception as e:
                logging.warning(f"Could not set restrictive permissions on .env file: {e}")
            
            logging.info("API Key saved to .env file")
            messagebox.showinfo("Success", "API Key saved to .env file successfully\nNote: For better security, consider using system credential storage.")
        except Exception as e:
            error_msg = f"Failed to update .env file: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def browse_file(self):
        filetypes = [
            ("Text files", "*.txt"),
            ("Word documents", "*.docx"),
            ("PDF files", "*.pdf"),
            ("All files", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.file_path_var.set(file_path)
            logging.info(f"File selected: {file_path}")
            self.load_file_preview(file_path)
    
    def browse_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_path_var.set(folder_path)
            logging.info(f"Output folder selected: {folder_path}")
            # Ensure folder exists
            Path(folder_path).mkdir(exist_ok=True)
    
    def load_file_preview(self, file_path):
        try:
            logging.info(f"Loading preview for file: {file_path}")
            text = self.read_input_file(Path(file_path))
            # Truncate if too long
            if len(text) > 1000:
                preview_text = text[:1000] + "...\n\n[File truncated for preview]"
                logging.info(f"File preview truncated, total length: {len(text)} characters")
            else:
                preview_text = text
                logging.info(f"File preview loaded, length: {len(text)} characters")
                
            self.file_preview.delete(1.0, tk.END)
            self.file_preview.insert(tk.END, preview_text)
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.file_preview.delete(1.0, tk.END)
            self.file_preview.insert(tk.END, error_msg)
    
    # Read .txt files
    def read_txt(self, file_path):
        logging.info(f"Reading TXT file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # Read .docx files
    def read_docx(self, file_path):
        logging.info(f"Reading DOCX file: {file_path}")
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    # Read .pdf files
    def read_pdf(self, file_path):
        logging.info(f"Reading PDF file: {file_path}")
        doc = fitz.open(file_path)
        return "\n".join([page.get_text() for page in doc])

    # Select reader based on file extension
    def read_input_file(self, file_path):
        if file_path.suffix.lower() == ".txt":
            return self.read_txt(file_path)
        elif file_path.suffix.lower() == ".docx":
            return self.read_docx(file_path)
        elif file_path.suffix.lower() == ".pdf":
            return self.read_pdf(file_path)
        else:
            error_msg = f"Unsupported file type: {file_path.suffix}"
            logging.error(error_msg)
            raise ValueError(error_msg)
    
    def get_input_text(self):
        """Get the input text based on the selected tab"""
        current_tab = self.tab_control.index(self.tab_control.select())
        if current_tab == 0:  # Text input tab
            text = self.text_input.get(1.0, tk.END).strip()
            if not text:
                return None
            return text
        else:  # File input tab
            file_path = self.file_path_var.get()
            if not file_path:
                return None
            
            try:
                text = self.read_input_file(Path(file_path))
                if not text or len(text.strip()) < 10:
                    return None
                return text
            except Exception as e:
                logging.error(f"Error reading file: {str(e)}", exc_info=True)
                return None

    def preview_audio(self):
        """Preview audio directly without saving to file"""
        logging.info("Starting audio preview")
        if not self.async_client:
            logging.warning("No async API client available, requesting API key")
            if not self.update_api_key():
                return
        
        # Get input text
        text = self.get_input_text()
        if not text:
            messagebox.showerror("Error", "Please enter text or select a file with content")
            return
        
        # Get a small sample of text for preview (first 150 chars or first paragraph)
        preview_text = text[:150]
        if "\n" in preview_text:
            preview_text = preview_text.split("\n")[0]
        
        # If preview text is too short, get more
        if len(preview_text) < 50 and len(text) > 50:
            preview_text = text[:100]
        
        # Get voice options
        voice = self.voice_var.get()
        model = self.model_var.get()
        instructions = self.instructions_text.get(1.0, tk.END).strip()
        
        # Log preview request
        preview_params = {
            "model": model,
            "voice": voice,
            "instructions": instructions,
            "preview_text_length": len(preview_text),
            "preview_text": preview_text
        }
        logging.info(f"Audio preview parameters: {json.dumps(preview_params, indent=2)}")
        
        # Set status and progress bar
        self.status_var.set("Riproducendo anteprima audio...")
        self.progress_bar.start()
        
        # Start preview in a separate thread to keep UI responsive
        threading.Thread(target=self._run_preview, args=(preview_text, voice, model, instructions), daemon=True).start()
    
    def _run_preview(self, text, voice, model, instructions):
        """Run the async preview in a separate thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._preview_audio_async(text, voice, model, instructions))
            loop.close()
            self.root.after(0, self._preview_complete, True, "")
        except Exception as e:
            error_msg = f"Error during audio preview: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.root.after(0, self._preview_complete, False, str(e))
    
    async def _preview_audio_async(self, text, voice, model, instructions):
        """Async function to preview audio"""
        logging.info("Making async API request for audio preview")
        try:
            async with self.async_client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=text,
                instructions=instructions,
                response_format="pcm",
            ) as response:
                logging.info(f"Preview response received. Status: {response.status_code}")
                await LocalAudioPlayer().play(response)
                logging.info("Audio preview completed")
        except Exception as e:
            logging.error(f"Error in async audio preview: {str(e)}", exc_info=True)
            raise e
    
    def _preview_complete(self, success, error_msg):
        """Update UI after preview completes"""
        self.progress_bar.stop()
        
        if success:
            self.status_var.set("Anteprima completata")
            logging.info("Audio preview completed successfully")
        else:
            self.status_var.set("Errore nell'anteprima")
            messagebox.showerror("Error", f"Failed to preview audio: {error_msg}")
            logging.error(f"Audio preview failed: {error_msg}")
    
    def generate_speech(self):
        logging.info("Starting speech generation process")
        if not self.client:
            logging.warning("No API client available, requesting API key")
            if not self.update_api_key():
                return
        
        # Get input text based on selected tab
        current_tab = self.tab_control.index(self.tab_control.select())
        if current_tab == 0:  # Text input tab
            text = self.text_input.get(1.0, tk.END).strip()
            if not text:
                logging.warning("No text entered in text input tab")
                messagebox.showerror("Error", "Please enter some text")
                return
            output_filename = "text_input.mp3"
            logging.info(f"Using direct text input, length: {len(text)} characters")
        else:  # File input tab
            file_path = self.file_path_var.get()
            if not file_path:
                logging.warning("No file selected in file input tab")
                messagebox.showerror("Error", "Please select a file")
                return
            
            try:
                logging.info(f"Reading file for speech generation: {file_path}")
                text = self.read_input_file(Path(file_path))
                if not text or len(text.strip()) < 10:
                    logging.warning(f"File is empty or too short: {file_path}")
                    messagebox.showerror("Error", "File is empty or too short")
                    return
                output_filename = Path(file_path).stem + ".mp3"
                logging.info(f"File read successfully, content length: {len(text)} characters")
            except Exception as e:
                error_msg = f"Error reading file: {str(e)}"
                logging.error(error_msg, exc_info=True)
                messagebox.showerror("Error", error_msg)
                return
        
        # Get output path
        output_dir = Path(self.output_path_var.get())
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / output_filename
        logging.info(f"Output will be saved to: {output_file}")
        
        # Check if output file exists
        if output_file.exists():
            logging.info(f"Output file already exists: {output_file}")
            if not messagebox.askyesno("File Exists", f"File {output_filename} already exists. Overwrite?"):
                logging.info("User chose not to overwrite existing file")
                return
            logging.info("User chose to overwrite existing file")
        
        # Get voice options
        voice = self.voice_var.get()
        model = self.model_var.get()
        instructions = self.instructions_text.get(1.0, tk.END).strip()
        
        # Log request parameters
        request_params = {
            "model": model,
            "voice": voice,
            "instructions": instructions,
            "text_length": len(text),
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "output_file": str(output_file)
        }
        logging.info(f"API Request parameters: {json.dumps(request_params, indent=2)}")
        
        # Start processing in a separate thread
        self.status_var.set("Generating speech...")
        self.progress_bar.start()
        logging.info("Starting speech generation thread")
        
        thread = threading.Thread(
            target=self._generate_speech_thread, 
            args=(text, output_file, voice, model, instructions)
        )
        thread.daemon = True
        thread.start()
    
    def _generate_speech_thread(self, text, output_file, voice, model, instructions):
        try:
            logging.info("Making API request to OpenAI TTS service")
            # Using the recommended streaming approach
            with self.client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=text,
                instructions=instructions
            ) as response:
                # Log response headers
                logging.info(f"Response received. Status: {response.status_code}")
                logging.info(f"Response headers: {dict(response.headers)}")
                
                # Save the streaming response to file
                bytes_written = 0
                with open(str(output_file), 'wb') as f:
                    for chunk in response.iter_bytes():
                        bytes_written += len(chunk)
                        f.write(chunk)
                
                logging.info(f"Audio file saved: {output_file}, Size: {bytes_written} bytes")
            
            # Update UI on the main thread
            self.root.after(0, lambda: self._processing_complete(True, output_file))
        except Exception as e:
            error_msg = f"Error generating speech: {str(e)}"
            logging.error(error_msg, exc_info=True)
            # Update UI on the main thread
            self.root.after(0, lambda: self._processing_complete(False, str(e)))
    
    def _processing_complete(self, success, result):
        self.progress_bar.stop()
        
        if success:
            msg = f"Audio saved to: {result}"
            self.status_var.set(msg)
            logging.info(msg)
            messagebox.showinfo("Success", f"Audio generated successfully and saved to:\n{result}")
            
            # Ask if user wants to open the logs folder
            if messagebox.askyesno("View Logs", "Would you like to open the logs folder to see the detailed request log?"):
                logs_dir = Path("logs").absolute()
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(logs_dir)
                    elif os.name == 'posix':  # macOS or Linux
                        import subprocess
                        subprocess.Popen(['open', logs_dir] if os.sys.platform == 'darwin' else ['xdg-open', logs_dir])
                    logging.info("Opened logs directory")
                except Exception as e:
                    error_msg = f"Could not open logs folder: {str(e)}"
                    messagebox.showerror("Error", error_msg)
                    logging.error(error_msg)
        else:
            error_msg = f"Failed to generate audio: {result}"
            self.status_var.set("Error generating audio")
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalTTSApp(root)
    root.mainloop()