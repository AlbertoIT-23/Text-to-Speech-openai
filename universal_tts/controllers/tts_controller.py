import logging
import threading
from pathlib import Path

class TTSController:
    """Controller for TTS operations"""
    
    def __init__(self, tts_model, file_model):
        self.tts_model = tts_model
        self.file_model = file_model
    
    def preview_audio(self, text, voice, model, instructions, speed, callback):
        """Preview audio with the given parameters"""
        # Validate inputs
        if not text:
            logging.error("No text provided for preview")
            if callback:
                callback(False, "No text provided")
            return
        
        # Validate voice-model compatibility
        if not self.tts_model.is_voice_compatible(voice, model):
            error_msg = f"Voice '{voice}' is not compatible with model '{model}'"
            logging.error(error_msg)
            if callback:
                callback(False, error_msg)
            return
        
        # Start preview
        logging.info(f"Previewing audio with voice '{voice}', model '{model}'")
        self.tts_model.preview_audio(text, voice, model, instructions, speed, callback)
    
    def generate_speech(self, text, output_dir, filename, voice, model, 
                        instructions=None, format="mp3", speed=1.0, callback=None):
        """Generate speech and save to a file"""
        # Validate inputs
        if not text:
            logging.error("No text provided for generation")
            if callback:
                callback(False, "No text provided")
            return
        
        # Validate voice-model compatibility
        if not self.tts_model.is_voice_compatible(voice, model):
            error_msg = f"Voice '{voice}' is not compatible with model '{model}'"
            logging.error(error_msg)
            if callback:
                callback(False, error_msg)
            return
        
        # Ensure output directory exists
        output_dir = self.file_model.ensure_output_directory(output_dir)
        output_file = output_dir / filename
        
        # Start generation in a separate thread
        def generate_speech_thread():
            try:
                result = self.tts_model.generate_speech(
                    text, output_file, voice, model, instructions, format, speed
                )
                if callback:
                    callback(True, result)
            except Exception as e:
                error_msg = f"Error generating speech: {str(e)}"
                logging.error(error_msg, exc_info=True)
                if callback:
                    callback(False, error_msg)
        
        thread = threading.Thread(target=generate_speech_thread)
        thread.daemon = True
        thread.start()