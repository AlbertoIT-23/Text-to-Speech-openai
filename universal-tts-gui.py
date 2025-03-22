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

# Add support for system credential manager
try:
    import keyring
    import getpass
    KEYRING_AVAILABLE = True
    SERVICE_NAME = "OpenAI-TTS-App"
    USERNAME = getpass.getuser()
except ImportError:
    KEYRING_AVAILABLE = False
    SERVICE_NAME = None
    USERNAME = None
    logging.warning("keyring package not available. Install with: pip install keyring")

# Load .env file
load_dotenv()

class ScrollableUniversalTTSApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Universal-TTS")  
        self.root.geometry("900x700")
        self.root.minsize(800, 550)
        
        # Set app theme colors
        self.colors = {
            "primary": "#1976D2",  # Main blue color
            "primary_dark": "#0D47A1",
            "accent": "#2E7D32",   # Green for action buttons
            "accent_dark": "#1B5E20",
            "bg_light": "#F5F5F5",
            "bg_dark": "#E0E0E0",
            "text": "#212121",
            "text_secondary": "#757575"
        }
        
        # Initialize API key using keyring if available
        self.api_key = self.get_api_key_from_sources()
        self.client = None
        self.async_client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.async_client = AsyncOpenAI(api_key=self.api_key)
        
        # Setup logging
        self.setup_logging()
        
        # Define voice details
        self.common_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.special_voices = ["ash", "ballad", "coral", "sage", "verse"]
        
        # Voice-model compatibility map
        self.voice_model_map = {
            "gpt-4o-mini-tts": self.common_voices + self.special_voices,
            "tts-1": self.common_voices + ["ash", "coral", "sage"],
            "tts-1-hd": self.common_voices + ["ash", "coral", "sage"]
        }
        
        # To track the source of the API key
        self.api_key_source = None
        
        # Set style
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 11))
        self.style.configure('TLabel', font=('Arial', 11))
        
        # Create the main layout with scrolling
        self.create_layout()

    def show_settings_dialog(self):
        """Show a settings dialog with API key management"""
        # Create a modal dialog
        settings_dialog = tk.Toplevel(self.root)
        settings_dialog.title("Config API Key")
        settings_dialog.transient(self.root)
        settings_dialog.grab_set()
        
        # Set dialog size - ridotta a dimensioni più compatte
        settings_dialog.geometry("500x320")  
        settings_dialog.minsize(500, 320)  
        settings_dialog.resizable(True, True)
        
        # Create dialog content
        content_frame = ttk.Frame(settings_dialog, padding="15")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key section
        api_frame = ttk.LabelFrame(content_frame, text="OpenAI API Key", padding="8")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        key_label_text = "Your API key is securely stored"
        if self.api_key_source:
            key_label_text += f" in {self.api_key_source}"
        key_label_text += ". You can update it below:"
        
        key_label = ttk.Label(api_frame, text=key_label_text, font=('Segoe UI', 9))
        key_label.pack(anchor=tk.W, pady=(0, 5))
        
        key_entry_frame = ttk.Frame(api_frame)
        key_entry_frame.pack(fill=tk.X)
        
        self.api_entry = ttk.Entry(key_entry_frame, show="•", width=45)
        if self.api_key:
            # Show only last 4 chars of actual key for reference
            masked_key = "•" * 20 + self.api_key[-4:] if len(self.api_key) > 4 else self.api_key
            self.api_entry.insert(0, masked_key)
        self.api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        show_key_var = tk.BooleanVar(value=False)
        
        def toggle_key_visibility():
            if show_key_var.get():
                self.api_entry.config(show="")
                if self.api_key and "•" in self.api_entry.get():
                    # Replace masked key with actual key
                    self.api_entry.delete(0, tk.END)
                    self.api_entry.insert(0, self.api_key)
            else:
                self.api_entry.config(show="•")
        
        show_key_check = ttk.Checkbutton(
            key_entry_frame, 
            text="Show", 
            variable=show_key_var,
            command=toggle_key_visibility
        )
        show_key_check.pack(side=tk.LEFT)
        
        key_note = ttk.Label(
            api_frame, 
            text="Note: Your API key is used to access OpenAI's text-to-speech services", 
            font=('Segoe UI', 8, 'italic'),
            foreground=self.colors["text_secondary"]
        )
        key_note.pack(anchor=tk.W, pady=(3, 0))
        
        # Storage options
        storage_frame = ttk.LabelFrame(content_frame, text="Storage Options", padding="8")
        storage_frame.pack(fill=tk.X, pady=(0, 10))
        
        storage_var = tk.StringVar(value="system" if KEYRING_AVAILABLE else "env")
        
        system_radio = ttk.Radiobutton(
            storage_frame, 
            text="Store in system credential manager (recommended)", 
            variable=storage_var, 
            value="system"
        )
        system_radio.pack(anchor=tk.W, pady=1)
        
        env_radio = ttk.Radiobutton(
            storage_frame, 
            text="Store in .env file", 
            variable=storage_var, 
            value="env"
        )
        env_radio.pack(anchor=tk.W, pady=1)
        
        session_radio = ttk.Radiobutton(
            storage_frame, 
            text="Use for this session only", 
            variable=storage_var, 
            value="session"
        )
        session_radio.pack(anchor=tk.W, pady=1)
        
        # Disable system option if not available
        if not KEYRING_AVAILABLE:
            system_radio.config(state="disabled")
            key_note = ttk.Label(
                storage_frame, 
                text="System credential storage unavailable. Install 'keyring' package for enhanced security.", 
                font=('Segoe UI', 8, 'italic'),
                foreground=self.colors["text_secondary"]
            )
            key_note.pack(anchor=tk.W, pady=(3, 0))
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(8, 0))
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=settings_dialog.destroy
        )
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_button = ttk.Button(
            button_frame, 
            text="Save API Key", 
            style="Primary.TButton",
            command=lambda: self.save_api_key(
                self.api_entry.get().strip(), 
                storage_var.get(),
                settings_dialog
            )
        )
        save_button.pack(side=tk.RIGHT)
        
        self._center_dialog(settings_dialog)
    
    def save_api_key(self, key, storage_method, dialog):
        """Save API key with the selected storage method"""
        if not key:
            messagebox.showerror("Error", "Please enter a valid API Key", parent=dialog)
            return
        
        # Remove any placeholder chars if present
        if "•" in key:
            # User didn't change the masked display
            if self.api_key:
                # Keep using existing key
                key = self.api_key
            else:
                messagebox.showerror("Error", "Please enter a valid API Key", parent=dialog)
                return
        
        # Update for current session
        os.environ["OPENAI_API_KEY"] = key
        self.api_key = key
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        
        # Store based on selected method
        if storage_method == "system" and KEYRING_AVAILABLE:
            try:
                keyring.set_password(SERVICE_NAME, USERNAME, key)
                messagebox.showinfo("Success", "API Key securely saved in system credential manager", parent=dialog)
                self.api_key_source = "system credential manager"
            except Exception as e:
                messagebox.showerror("Error", f"Could not save to credential manager: {e}", parent=dialog)
        
        elif storage_method == "env":
            try:
                env_path = Path(".env")
                
                # If .env exists, read and update it
                if env_path.exists():
                    with open(env_path, "r") as f:
                        lines = f.readlines()
                    
                    found = False
                    for i, line in enumerate(lines):
                        if line.startswith("OPENAI_API_KEY="):
                            lines[i] = f"OPENAI_API_KEY={key}\n"
                            found = True
                            break
                    
                    if not found:
                        lines.append(f"OPENAI_API_KEY={key}\n")
                    
                    with open(env_path, "w") as f:
                        f.writelines(lines)
                else:
                    # Create new .env file
                    with open(env_path, "w") as f:
                        f.write(f"OPENAI_API_KEY={key}\n")
                
                messagebox.showinfo("Success", "API Key saved to .env file", parent=dialog)
                self.api_key_source = ".env file"
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update .env file: {e}", parent=dialog)
        
        elif storage_method == "session":
            messagebox.showinfo("Success", "API Key updated for this session only", parent=dialog)
            self.api_key_source = "current session only"
        
        # Close the dialog
        dialog.destroy()

    def _toggle_api_key_visibility(self):
        """Toggle showing or hiding the API key"""
        if self.show_key_var.get():
            self.api_entry.config(show="")
        else:
            self.api_entry.config(show="*")

    def _center_dialog(self, dialog):
        """Center a dialog on its parent window"""
        dialog.update_idletasks()
        
        # Get parent and dialog dimensions
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        
        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Set position
        dialog.geometry(f"+{x}+{y}")
    
    def setup_logging(self):
        """Setup logging to file with enhanced error checking"""
        try:
            # Reset any existing logger configuration first
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
                
            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            try:
                logs_dir.mkdir(exist_ok=True)
                print(f"Logs directory: {logs_dir.absolute()} {'exists' if logs_dir.exists() else 'creation failed'}")
            except Exception as dir_err:
                print(f"Error creating logs directory: {dir_err}")
                logs_dir = Path(".")
            
            # Create a log file with timestamp in name
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = logs_dir / f"tts_log_{timestamp}.log"
            
            print(f"Attempting to create log file: {log_file.absolute()}")
            
            # Test if we can write to the file
            try:
                with open(log_file, 'w') as f:
                    f.write(f"Log started at {datetime.datetime.now().isoformat()}\n")
                print(f"Log file created successfully: {log_file}")
            except Exception as file_err:
                print(f"Cannot write to log file: {file_err}")
                log_file = Path(f"./tts_log_{timestamp}.log")
                try:
                    with open(log_file, 'w') as f:
                        f.write(f"Log started at {datetime.datetime.now().isoformat()}\n")
                    print(f"Created fallback log file: {log_file}")
                except Exception as fallback_err:
                    print(f"Cannot create fallback log file: {fallback_err}")
                    return False
            
            # Configure basic logging
            logging.basicConfig(
                filename=str(log_file),
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filemode='w'  # Overwrite if exists
            )
            
            # Add console handler for informational messages
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console.setFormatter(formatter)
            
            # Make sure we don't add duplicate handlers
            root_logger = logging.getLogger('')
            has_console = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
            if not has_console:
                root_logger.addHandler(console)
                
            # Log startup information
            logging.info(f"Logging initialized to: {log_file}")
            logging.info(f"Application started at: {datetime.datetime.now().isoformat()}")
            logging.info(f"Python version: {os.sys.version}")
            logging.info(f"Operating system: {os.name} - {os.sys.platform}")
            
            print(f"Logging to: {log_file}")
            return True
            
        except Exception as e:
            print(f"Critical error in setup_logging: {e}")
            # Fallback to console-only logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            print("Fallback to console logging only")
            return False
    
    def create_layout(self):
        """Create the main layout with scrollable content and fixed controls"""
        # Main container - using grid for better control
        self.root.grid_rowconfigure(0, weight=1)  # Content area expands
        self.root.grid_rowconfigure(1, weight=0)  # Fixed height for bottom controls
        self.root.grid_columnconfigure(0, weight=1)  # Full width
        
        # Create main frame that will contain the scrollable content
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Header row with title and API Key button
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Title area 
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill=tk.X)
        title_frame.columnconfigure(0, weight=1)  # Make title expand
        
        # Title label with new app name
        title_label = ttk.Label(title_frame, text="Universal-TTS   AI Voice", font=('Segoe UI', 12, 'bold'))
        title_label.grid(row=0, column=0, sticky="w")
        
        # Settings button
        settings_button = tk.Button(
            title_frame, 
            text="⚙️ Config API Key",
            command=self.show_settings_dialog,
            font=('Segoe UI', 10),
            background=self.colors["primary"],
            foreground="white",
            activebackground=self.colors["primary_dark"],
            activeforeground="white",
            relief=tk.RAISED,
            borderwidth=1,
            padx=10,
            pady=2,
            cursor="hand2"
        )
        settings_button.grid(row=0, column=1, sticky="e", padx=(10, 20))
        
        # Create scrollable frame for main content
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create canvas with scrollbar
        self.canvas = tk.Canvas(canvas_frame, bg=self.colors["bg_light"])
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Make the scrollable frame resize with the canvas width
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Create a window into the canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas and scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add content to the scrollable frame
        self.create_scrollable_content()
        
        # Bottom controls in a fixed frame
        self.bottom_frame = ttk.Frame(self.root, padding="10")
        self.bottom_frame.grid(row=1, column=0, sticky="ew")

        # Configure columns for flexible layout
        self.bottom_frame.columnconfigure(0, weight=1)  # Spazio flessibile a sinistra
        self.bottom_frame.columnconfigure(1, weight=2)  # Status al centro (più largo)
        self.bottom_frame.columnconfigure(2, weight=1)  # Spazio flessibile a destra

        # Status and buttons
        status_frame = ttk.Frame(self.bottom_frame)
        status_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.status_var = tk.StringVar(value="Ready")
        # Status label
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 9))
        status_label.pack(side=tk.LEFT, padx=(0, 10))

        # Progress bar
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate', length=80)
        self.progress_bar.pack(side=tk.LEFT)

        # Buttons on the right
        buttons_frame = ttk.Frame(self.bottom_frame)
        buttons_frame.grid(row=0, column=2, sticky="e")
        
        # Preview button
        preview_button = tk.Button(
            buttons_frame, 
            text="▶ Preview Audio",
            command=self.preview_audio,
            font=('Arial', 10),
            background=self.colors["primary"],
            foreground='white',
            activebackground=self.colors["primary_dark"],
            activeforeground='white',
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,  
            pady=5,
            cursor="hand2",
            width=12  
        )
        preview_button.pack(side=tk.LEFT, padx=(0, 25))
        
        # Generate button
        generate_button = tk.Button(
            buttons_frame,
            text="GENERATE AUDIO FILE",
            command=self.generate_speech,
            font=('Arial', 10, 'bold'),
            background=self.colors["accent"],
            foreground='white',
            activebackground=self.colors["accent_dark"],
            activeforeground='white',
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,  
            pady=5,
            cursor="hand2",
            width=18
        )
        generate_button.pack(side=tk.RIGHT, padx=(0, 20))
    
    def on_canvas_configure(self, event):
        """Adjust the width of the scrollable frame when the canvas changes size"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def create_scrollable_content(self):
        """Create all the content that goes in the scrollable area"""
        # Input method tabs
        self.tab_control = ttk.Notebook(self.scrollable_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tab 1: Direct Text Input
        text_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(text_tab, text="Text Input")
        
        text_label = ttk.Label(text_tab, text="Enter or paste text:")
        text_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.text_input = scrolledtext.ScrolledText(text_tab, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_input.insert(tk.END, "Welcome to the Universal Text-to-Speech tool. This is a simple example of what you can create with OpenAI's speech synthesis API. You can customize the voice, tone, and style to suit your needs.")
        
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
        
        # Voice options frame with grid layout
        voice_frame = ttk.LabelFrame(self.scrollable_frame, text="Voice Options", padding="10")
        voice_frame.pack(fill=tk.X, padx=5, pady=5)

        # Voice selection
        voice_label = ttk.Label(voice_frame, text="Voice:")
        voice_label.grid(row=0, column=0, sticky=tk.W, padx=(5, 0), pady=5)

        # Create voice display options with asterisks for special voices
        voice_display_options = []
        for voice in self.voice_model_map["gpt-4o-mini-tts"]:
            if voice in self.special_voices:
                voice_display_options.append(f"{voice} *")
            else:
                voice_display_options.append(voice)
        
        self.voice_var = tk.StringVar(value="alloy")  # Default voice
        self.voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, values=voice_display_options, width=15, state="readonly")
        self.voice_dropdown.grid(row=0, column=0, sticky=tk.W, padx=(60, 5), pady=5) 
        
        # Add note about special voices
        voice_special_note = ttk.Label(voice_frame, text="* = Special voices with enhanced capabilities", 
                                font=('Arial', 8, 'italic'), foreground='#666666')
        voice_special_note.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 5))

        # Model selection
        model_label = ttk.Label(voice_frame, text="Model:")
        model_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

        self.model_var = tk.StringVar(value="gpt-4o-mini-tts")
        model_options = ["gpt-4o-mini-tts", "tts-1", "tts-1-hd"]
        model_dropdown = ttk.Combobox(voice_frame, textvariable=self.model_var, values=model_options, width=17, state="readonly")
        model_dropdown.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        model_dropdown.bind("<<ComboboxSelected>>", self.update_voice_options)

        # Format selection
        format_label = ttk.Label(voice_frame, text="Format:")
        format_label.grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)

        self.format_var = tk.StringVar(value="mp3")
        format_options = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
        format_dropdown = ttk.Combobox(voice_frame, textvariable=self.format_var, values=format_options, width=8, state="readonly")
        format_dropdown.grid(row=0, column=5, sticky=tk.W, padx=5, pady=5)

        # Speed selection
        speed_label = ttk.Label(voice_frame, text="Speed:")
        speed_label.grid(row=0, column=6, sticky=tk.W, padx=(5, 0), pady=5)

        self.speed_var = tk.StringVar(value="1.00")
        speed_options = ["0.25", "0.50", "0.75", "0.85", "0.90", "0.95", "1.00", "1.05", "1.10", "1.15", "1.20", "1.25", "1.50", "1.75", "2.00", "3.00", "4.00"]
        speed_dropdown = ttk.Combobox(voice_frame, textvariable=self.speed_var, values=speed_options, width=5, state="readonly")
        speed_dropdown.grid(row=0, column=6, sticky=tk.W, padx=(70, 5), pady=5)
        
        # Add note about speed compatibility
        speed_note = ttk.Label(voice_frame, text="Speed only works with tts-1 and tts-1-hd models", 
                            font=('Arial', 8, 'italic'), foreground='#666666')
        speed_note.grid(row=1, column=6, columnspan=2, sticky=tk.W, padx=5, pady=(0, 5))
        
        # Configure voice_frame columns to properly distribute space
        voice_frame.columnconfigure(0, weight=0)  
        voice_frame.columnconfigure(1, weight=1)  
        voice_frame.columnconfigure(2, weight=0)  
        voice_frame.columnconfigure(3, weight=1)  
        voice_frame.columnconfigure(4, weight=0)  
        voice_frame.columnconfigure(5, weight=0)  
        voice_frame.columnconfigure(6, weight=0)  
        voice_frame.columnconfigure(7, weight=0)  
        
        # Voice instructions
        instructions_label = ttk.Label(voice_frame, text="Voice instructions:")
        instructions_label.grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        
        self.instructions_text = scrolledtext.ScrolledText(voice_frame, height=6, wrap=tk.WORD)
        self.instructions_text.grid(row=3, column=0, columnspan=8, sticky=tk.NSEW, padx=5, pady=5)
        self.instructions_text.insert(tk.END, "Speak clearly, with a warm and narrative tone.")
        
        # Output options
        output_frame = ttk.LabelFrame(self.scrollable_frame, text="Output Options", padding="10")
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        output_path_label = ttk.Label(output_frame, text="Output folder:")
        output_path_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.output_path_var = tk.StringVar(value=str(Path("output")))
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=40)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        output_browse = ttk.Button(output_frame, text="Browse", command=self.browse_output_folder)
        output_browse.pack(side=tk.LEFT, padx=(0, 5))
    
    def update_voice_options(self, event=None):
        """Update voice dropdown options based on selected model"""
        selected_model = self.model_var.get()
        current_voice = self.voice_var.get()
        
        # Remove asterisk if present
        if " *" in current_voice:
            base_voice = current_voice.replace(" *", "")
        else:
            base_voice = current_voice
        
        # Get voices compatible with the selected model
        available_voices = self.voice_model_map.get(selected_model, [])
        
        # Create display options with asterisks for special voices
        display_options = []
        for voice in available_voices:
            if voice in self.special_voices:
                display_options.append(f"{voice} *")  # Add asterisk for special voices
            else:
                display_options.append(voice)
        
        # Update dropdown values
        self.voice_dropdown['values'] = display_options
        
        # If current voice is not compatible with new model, reset to first available
        if base_voice not in available_voices:
            if available_voices:
                # Set to first available voice
                if available_voices[0] in self.special_voices:
                    self.voice_var.set(f"{available_voices[0]} *")
                else:
                    self.voice_var.set(available_voices[0])
                logging.info(f"Voice changed to {available_voices[0]} as {base_voice} is not compatible with {selected_model}")
            else:
                logging.warning(f"No voices available for model {selected_model}")
        else:
            # Update current selection in case asterisk needs to be added/removed
            for i, voice in enumerate(available_voices):
                if voice == base_voice:
                    self.voice_var.set(display_options[i])
                    break
    
    def get_api_key_from_sources(self):
        """Try different sources to obtain API key in order of security."""
        # 1. First try environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logging.info("API key found in environment variable")
            return api_key
            
        # 2. Try system credential manager if available
        if KEYRING_AVAILABLE:
            try:
                api_key = keyring.get_password(SERVICE_NAME, USERNAME)
                if api_key:
                    logging.info("API key found in system credential manager")
                    return api_key
            except Exception as e:
                logging.warning(f"Error accessing system credentials: {e}")
        
        # 3. Fallback: try .env file (less secure)
        # load_dotenv() was already called at the beginning
        
        logging.info("No API key found in any secure storage")
        return None
    
    def update_api_key(self):
        """Update the API key and optionally save it for future use"""
        new_key = self.api_entry.get().strip()
        if new_key:
            # Update for current session
            os.environ["OPENAI_API_KEY"] = new_key
            self.api_key = new_key
            self.client = OpenAI(api_key=self.api_key)
            self.async_client = AsyncOpenAI(api_key=self.api_key)
            logging.info("API Key updated for current session")
            
            # Simplified version with explicit choices
            if KEYRING_AVAILABLE:
                # First question: do you want to save the key for future use?
                save_choice = messagebox.askyesno(
                    "Save API Key",
                    "API Key updated for this session.\n\n"
                    "Do you want to save the key for future use?\n\n"
                    "• YES = Save for future use\n"
                    "• NO = Use only for this session",
                    icon=messagebox.QUESTION
                )
                
                if save_choice:
                    # Second question: which storage method do you prefer?
                    secure_choice = messagebox.askyesno(
                        "Storage Method",
                        "Which storage method do you prefer?\n\n"
                        "• YES = Save in system credential manager (recommended)\n"
                        "• NO = Save in a .env file (less secure)",
                        icon=messagebox.QUESTION
                    )
                    
                    if secure_choice:
                        # Save to credential manager
                        try:
                            keyring.set_password(SERVICE_NAME, USERNAME, new_key)
                            messagebox.showinfo("Success", 
                                              "API Key securely saved in system credential manager")
                        except Exception as e:
                            messagebox.showerror("Error", 
                                               f"Could not save to credential manager: {e}")
                    else:
                        # Save to .env file
                        self._save_to_env_file(new_key)
                else:
                    # Session only
                    messagebox.showinfo("Success", 
                                      "API Key updated for this session only")
            else:
                # Simplified version without keyring
                if messagebox.askyesno(
                    "Save API Key",
                    "API Key updated for this session.\n\n"
                    "Do you want to save the key in a .env file for future use?\n\n"
                    "• YES = Save in .env file\n"
                    "• NO = Use only for this session\n\n"
                    "For better security, consider installing the 'keyring' package:\n"
                    "pip install keyring",
                    icon=messagebox.QUESTION
                ):
                    self._save_to_env_file(new_key)
                else:
                    messagebox.showinfo("Success", 
                                      "API Key updated for this session only")
            
            return True
        else:
            messagebox.showerror("Error", "Please enter a valid API Key")
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
            
            # Try to make the file accessible only to the current user
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
        """Browse for input file"""
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
        """Browse for output folder"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_path_var.set(folder_path)
            logging.info(f"Output folder selected: {folder_path}")
            # Ensure folder exists
            Path(folder_path).mkdir(exist_ok=True)
    
    def load_file_preview(self, file_path):
        """Load and display preview of selected file"""
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
        
        # Get a small sample of text for preview (first 190 chars or first paragraph)
        preview_text = text[:190]
        if "\n" in preview_text:
            preview_text = preview_text.split("\n")[0]
        
        # If preview text is too short, get more
        if len(preview_text) < 50 and len(text) > 50:
            preview_text = text[:100]
        
        # Get voice options
        voice = self.voice_var.get()
        # Remove asterisk if present
        if " *" in voice:
            voice = voice.replace(" *", "")
        
        model = self.model_var.get()
        format = self.format_var.get()  # Get selected format
        speed = float(self.speed_var.get())  # Convert to float
        instructions = self.instructions_text.get(1.0, tk.END).strip()

        # Log preview request
        preview_params = {
            "model": model,
            "voice": voice,
            "format": format,  # Add format to logging
            "speed": speed,    # Add speed to logging
            "instructions": instructions,
            "preview_text_length": len(preview_text),
            "preview_text": preview_text
        }
        logging.info(f"Audio preview parameters: {json.dumps(preview_params, indent=2)}")
        
        # Set status and progress bar
        self.status_var.set("Playing audio preview...")
        self.progress_bar.start()
        
        # Start preview in a separate thread to keep UI responsive
        threading.Thread(target=self._run_preview, args=(preview_text, voice, model, instructions), daemon=True).start()
    
    def _run_preview(self, text, voice, model, instructions):
        """Run the async preview in a separate thread"""
        try:
            speed = float(self.speed_var.get())  # Get speed parameter
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Pass speed parameter to the async method
            loop.run_until_complete(self._preview_audio_async(text, voice, model, instructions, speed))
            loop.close()
            self.root.after(0, self._preview_complete, True, "")
        except Exception as e:
            error_msg = f"Error during audio preview: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.root.after(0, self._preview_complete, False, error_msg)
    
    async def _preview_audio_async(self, text, voice, model, instructions, speed):
        """Async function to preview audio"""
        logging.info("Making async API request for audio preview")
        
        # Remove asterisk if present
        if " *" in voice:
            voice = voice.replace(" *", "")

        try:
            # Create API parameters
            api_params = {
                "model": model,
                "voice": voice,
                "input": text,
                "response_format": "pcm"  # Keep pcm for preview
            }
            
            # Add instructions if provided
            if instructions:
                api_params["instructions"] = instructions
            
            # Add speed parameter only for compatible models
            if model in ["tts-1", "tts-1-hd"]:
                api_params["speed"] = speed
                logging.info(f"Using speed {speed} with compatible model {model}")
            else:
                logging.info(f"Speed parameter ignored for model {model} (only works with tts-1 and tts-1-hd)")
            
            async with self.async_client.audio.speech.with_streaming_response.create(**api_params) as response:
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
            self.status_var.set("Preview completed")
            logging.info("Audio preview completed successfully")
        else:
            self.status_var.set("Error in preview")
            messagebox.showerror("Error", f"Failed to preview audio: {error_msg}")
            logging.error(f"Audio preview failed: {error_msg}")
    
    def generate_speech(self):
        """Generate speech and save to file"""
        logging.info("Starting speech generation process")
        if not self.client:
            logging.warning("No API client available, requesting API key")
            if not self.update_api_key():
                return
            
        # Get voice options
        voice = self.voice_var.get()
        # Remove asterisk if present
        if " *" in voice:
            voice = voice.replace(" *", "")
        
        model = self.model_var.get()
        
        # Validate voice-model compatibility
        voice_base = voice  # voice is already cleaned above
        if voice_base not in self.voice_model_map.get(model, []):
            error_msg = f"Voice '{voice_base}' is not compatible with model '{model}'. Please select a compatible voice."
            logging.error(error_msg)
            messagebox.showerror("Compatibility Error", error_msg)
            return
        
        # Get input text based on selected tab
        current_tab = self.tab_control.index(self.tab_control.select())
        
        # Get the format for the output file
        format = self.format_var.get()
        
        # Generate timestamp for the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if current_tab == 0:  # Text input tab
            text = self.text_input.get(1.0, tk.END).strip()
            if not text:
                logging.warning("No text entered in text input tab")
                messagebox.showerror("Error", "Please enter some text")
                return
            output_filename = f"speech_{voice}_{timestamp}.{format}"  # Include voice name and timestamp
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
                filename_base = Path(file_path).stem
                output_filename = f"{filename_base}_{voice}_{timestamp}.{format}"  # Include file name, voice name and timestamp
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
        
        # Since we're now using a timestamp, file should always be unique
        # But we'll keep the check just in case
        if output_file.exists():
            logging.info(f"Output file already exists: {output_file}")
            if not messagebox.askyesno("File Exists", f"File {output_filename} already exists. Overwrite?"):
                logging.info("User chose not to overwrite existing file")
                return
            logging.info("User chose to overwrite existing file")
        
        # Get voice options
        voice = self.voice_var.get()
        model = self.model_var.get()
        format = self.format_var.get()
        speed = float(self.speed_var.get())
        instructions = self.instructions_text.get(1.0, tk.END).strip()
        
        # Log request parameters
        request_params = {
            "model": model,
            "voice": voice,
            "format": format,
            "speed": speed,
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
            args=(text, output_file, voice, model, instructions, format, speed)
        )
        thread.daemon = True
        thread.start()
    
    def _generate_speech_thread(self, text, output_file, voice, model, instructions, format, speed):
        """Run the speech generation in a separate thread"""
        try:
            logging.info("Making API request to OpenAI TTS service")
            
            if " *" in voice:
                voice = voice.replace(" *", "")
            
            # Create API parameters
            api_params = {
                "model": model,
                "voice": voice,
                "input": text,
                "response_format": format
            }
            
            # Add instructions if provided
            if instructions:
                api_params["instructions"] = instructions
                
            # Add speed parameter only for compatible models
            if model in ["tts-1", "tts-1-hd"]:
                api_params["speed"] = speed
                logging.info(f"Using speed {speed} with compatible model {model}")
            else:
                logging.info(f"Speed parameter ignored for model {model} (only works with tts-1 and tts-1-hd)")
            
            logging.info(f"API call parameters: {json.dumps(api_params, indent=2)}")
            
            # Using the recommended streaming approach
            with self.client.audio.speech.with_streaming_response.create(**api_params) as response:
                # Log response headers
                logging.info(f"Response received. Status: {response.status_code}")
                
                # Save the streaming response to file
                bytes_written = 0
                with open(str(output_file), 'wb') as f:
                    for chunk in response.iter_bytes():
                        bytes_written += len(chunk)
                        f.write(chunk)
                
                logging.info(f"Audio file saved: {output_file}, Size: {bytes_written} bytes")
            
            # Update UI on the main thread
            self.root.after(0, self._processing_complete, True, output_file)
        except Exception as e:
            error_msg = f"Error generating speech: {str(e)}"
            logging.error(error_msg, exc_info=True)
            # Update UI on the main thread
            self.root.after(0, self._processing_complete, False, error_msg)
    
    def _processing_complete(self, success, result):
        """Update UI after generation completes"""
        self.progress_bar.stop()
        
        if success:
            # Show only the filename (not the complete path)
            file_name = os.path.basename(str(result))
            msg = f"Saved: {file_name}"
            self.status_var.set(msg)
            logging.info(f"Audio saved to: {result}")
            
            # Create a custom centered success dialog with smaller dimensions
            info_dialog = tk.Toplevel(self.root)
            info_dialog.title("Success")
            info_dialog.transient(self.root)
            info_dialog.grab_set()
            
            # Set size and properties - significantly reduced size
            info_dialog.geometry("450x160") 
            info_dialog.resizable(False, False)
            
            # Container frame with minimal padding
            frame = ttk.Frame(info_dialog, padding=8)  # Reduced padding from 10 to 8
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Success message with slightly smaller font
            ttk.Label(frame, text="Audio generated successfully!", 
                     font=("Segoe UI", 10, "bold")).pack(pady=(2, 2))  # Minimal padding
            
            # Saved file path with minimal padding
            ttk.Label(frame, text="Saved to:").pack(pady=(0, 1))  # Minimal padding
            ttk.Label(frame, text=f"{result}", wraplength=430).pack(pady=(0, 8))  # Reduced padding and wrap width
            
            # OK button at the bottom with no extra space
            button_frame = ttk.Frame(frame)
            button_frame.pack(fill=tk.X, expand=False, pady=(0, 0))  # No bottom padding
            
            # OK button centered
            ok_button = ttk.Button(button_frame, text="OK", command=info_dialog.destroy, width=8)
            ok_button.pack(pady=(20, 0))  # No padding
            
            # Center the dialog relative to the main window
            self._center_dialog(info_dialog)
        else:
            # Error handling
            error_msg = f"Failed to generate audio: {result}"
            self.status_var.set("Error generating audio")
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScrollableUniversalTTSApp(root)
    root.mainloop()