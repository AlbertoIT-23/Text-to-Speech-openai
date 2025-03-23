import os
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import datetime
import threading

from models.tts_model import TTSModel
from models.file_model import FileModel
from models.settings_model import SettingsModel
from views.main_view import MainView
from controllers.settings_controller import SettingsController
from utils.logging_config import setup_logging

class AppController:
    """Main application controller that coordinates models and views"""
    
    def __init__(self, root):
        """Initialize the application controller"""
        self.root = root
        
        # Setup logging first
        self.setup_logging()
        
        # Initialize models
        self.settings_model = SettingsModel()
        self.file_model = FileModel()
        self.tts_model = TTSModel(self.settings_model.api_key)
        
        # Initialize main view
        self.main_view = MainView(root, self)
        
        # Log startup information
        logging.info("Application started successfully")
        logging.info(f"API key available: {bool(self.settings_model.api_key)}")
    
    def setup_logging(self):
        """Setup application logging"""
        setup_logging()
    
    def show_settings_dialog(self):
        """Show the settings dialog"""
        settings_controller = SettingsController(
            self.root,
            self.settings_model,
            self.tts_model
        )
        settings_controller.show_dialog()
    
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
            self.main_view.file_input_view.file_path_var.set(file_path)
            logging.info(f"File selected: {file_path}")
            self.load_file_preview(file_path)
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.main_view.output_path_var.set(folder_path)
            logging.info(f"Output folder selected: {folder_path}")
            # Ensure folder exists
            Path(folder_path).mkdir(exist_ok=True)
    
    def load_file_preview(self, file_path):
        """Load and display preview of selected file"""
        try:
            logging.info(f"Loading preview for file: {file_path}")
            text = self.file_model.read_file(Path(file_path))
            # Truncate if too long
            if len(text) > 1000:
                preview_text = text[:1000] + "...\n\n[File truncated for preview]"
                logging.info(f"File preview truncated, total length: {len(text)} characters")
            else:
                preview_text = text
                logging.info(f"File preview loaded, length: {len(text)} characters")
                
            self.main_view.file_input_view.update_preview(preview_text)
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.main_view.file_input_view.update_preview(error_msg)
    
    def update_voice_options(self):
        """Update voice options based on the selected model"""
        model = self.main_view.model_var.get()
        available_voices = self.tts_model.get_available_voices(model)
        self.main_view.update_voice_options(available_voices)
        
        # Check if current voice is compatible
        current_voice = self.main_view.voice_var.get()
        
        # Remove asterisk if present
        if " *" in current_voice:
            base_voice = current_voice.replace(" *", "")
        else:
            base_voice = current_voice
        
        # If current voice is not compatible with new model, reset to first available
        if base_voice not in available_voices:
            if available_voices:
                # Get first available voice
                first_voice = available_voices[0]
                # Add asterisk if special
                if first_voice in self.tts_model.special_voices:
                    self.main_view.voice_var.set(f"{first_voice} *")
                else:
                    self.main_view.voice_var.set(first_voice)
                logging.info(f"Voice changed to {first_voice} as {base_voice} is not compatible with {model}")
    
    def get_input_text(self):
        """Get the input text based on the selected tab"""
        current_tab = self.main_view.get_current_tab()
        if current_tab == 0:  # Text input tab
            text = self.main_view.text_input_view.get_text()
            if not text:
                return None
            return text
        else:  # File input tab
            file_path = self.main_view.file_input_view.get_selected_file()
            if not file_path:
                return None
            
            try:
                text = self.file_model.read_file(Path(file_path))
                if not text or len(text.strip()) < 10:
                    return None
                return text
            except Exception as e:
                logging.error(f"Error reading file: {str(e)}", exc_info=True)
                return None

    def preview_audio(self):
            """Preview audio directly without saving to file"""
            logging.info("Starting audio preview")
            if not self.tts_model.async_client:
                logging.warning("No async API client available, requesting API key")
                messagebox.showerror("Error", "API key not configured. Please configure your API key first.")
                self.show_settings_dialog()
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
            voice = self.main_view.voice_var.get()
            model = self.main_view.model_var.get()
            speed = float(self.main_view.speed_var.get())  # Convert to float
            instructions = self.main_view.instructions_text.get(1.0, tk.END).strip()
            
            # Set status and progress bar
            self.main_view.start_progress("Playing audio preview...")
            
            # Start preview with callback for completion
            self.tts_model.preview_audio(
                preview_text, 
                voice, 
                model, 
                instructions, 
                speed,
                callback=self._preview_complete
            )
        
    def _preview_complete(self, success, error_msg):
        """Callback for when preview completes"""
        if success:
            self.main_view.stop_progress("Preview completed")
            logging.info("Audio preview completed successfully")
        else:
            self.main_view.stop_progress("Error in preview")
            messagebox.showerror("Error", f"Failed to preview audio: {error_msg}")
            logging.error(f"Audio preview failed: {error_msg}")
    
    def generate_speech(self):
        """Generate speech and save to file"""
        logging.info("Starting speech generation process")
        if not self.tts_model.client:
            logging.warning("No API client available, requesting API key")
            messagebox.showerror("Error", "API key not configured. Please configure your API key first.")
            self.show_settings_dialog()
            return
            
        # Get voice options
        voice = self.main_view.voice_var.get()
        model = self.main_view.model_var.get()
        
        # Validate voice-model compatibility
        if not self.tts_model.is_voice_compatible(voice, model):
            error_msg = f"Voice '{voice}' is not compatible with model '{model}'. Please select a compatible voice."
            logging.error(error_msg)
            messagebox.showerror("Compatibility Error", error_msg)
            return
        
        # Get input text
        text = self.get_input_text()
        if not text:
            logging.warning("No valid input text for speech generation")
            messagebox.showerror("Error", "Please enter valid text or select a file with content")
            return
        
        # Get the format for the output file
        format = self.main_view.format_var.get()
        
        # Generate output filename
        current_tab = self.main_view.get_current_tab()
        if current_tab == 0:  # Text input
            output_filename = self.file_model.generate_output_filename(
                voice=voice, 
                format=format
            )
            logging.info(f"Using direct text input, length: {len(text)} characters")
        else:  # File input
            file_path = self.main_view.file_input_view.get_selected_file()
            output_filename = self.file_model.generate_output_filename(
                input_filename=file_path,
                voice=voice, 
                format=format
            )
            logging.info(f"Using file input: {file_path}")
        
        # Get output path
        output_dir = Path(self.main_view.output_path_var.get())
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / output_filename
        logging.info(f"Output will be saved to: {output_file}")
        
        # Since we're using a timestamp, file should always be unique
        # But we'll keep the check just in case
        if output_file.exists():
            logging.info(f"Output file already exists: {output_file}")
            if not messagebox.askyesno("File Exists", f"File {output_filename} already exists. Overwrite?"):
                logging.info("User chose not to overwrite existing file")
                return
            logging.info("User chose to overwrite existing file")
        
        # Get remaining options
        speed = float(self.main_view.speed_var.get())
        instructions = self.main_view.instructions_text.get(1.0, tk.END).strip()
        
        # Start processing in a separate thread
        self.main_view.start_progress("Generating speech...")
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
            output_file = self.tts_model.generate_speech(
                text, 
                output_file, 
                voice, 
                model, 
                instructions, 
                format, 
                speed
            )
            
            # Update UI on the main thread
            self.root.after(0, self._processing_complete, True, output_file)
        except Exception as e:
            error_msg = f"Error generating speech: {str(e)}"
            logging.error(error_msg, exc_info=True)
            # Update UI on the main thread
            self.root.after(0, self._processing_complete, False, error_msg)
    
    def _processing_complete(self, success, result):
        """Update UI after generation completes"""
        if success:
            # Show only the filename (not the complete path)
            file_name = os.path.basename(str(result))
            msg = f"Saved: {file_name}"
            self.main_view.stop_progress(msg)
            logging.info(f"Audio saved to: {result}")
            
            # Show success dialog
            self.main_view.show_success_dialog(result)
        else:
            # Error handling
            error_msg = f"Failed to generate audio: {result}"
            self.main_view.stop_progress("Error generating audio")
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)