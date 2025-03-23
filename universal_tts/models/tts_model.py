import json
import logging
from pathlib import Path
from openai import OpenAI, AsyncOpenAI
from openai.helpers import LocalAudioPlayer
import asyncio
import threading

class TTSModel:
    """Model for handling TTS API operations and data"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = None
        self.async_client = None
        
        # Define voice details
        self.common_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.special_voices = ["ash", "ballad", "coral", "sage", "verse"]
        
        # Voice-model compatibility map
        self.voice_model_map = {
            "gpt-4o-mini-tts": self.common_voices + self.special_voices,
            "tts-1": self.common_voices + ["ash", "coral", "sage"],
            "tts-1-hd": self.common_voices + ["ash", "coral", "sage"]
        }
        
        # Initialize clients if API key is provided
        self.update_clients()

    def update_clients(self):
        """Update OpenAI clients with current API key"""
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.async_client = AsyncOpenAI(api_key=self.api_key)
            return True
        return False

    def set_api_key(self, api_key):
        """Set API key and reinitialize clients"""
        self.api_key = api_key
        return self.update_clients()

    def get_available_voices(self, model):
        """Get voices compatible with the selected model"""
        return self.voice_model_map.get(model, [])

    def is_voice_compatible(self, voice, model):
        """Check if a voice is compatible with a model"""
        # Remove asterisk if present
        if " *" in voice:
            voice = voice.replace(" *", "")
        return voice in self.voice_model_map.get(model, [])

    def generate_speech(self, text, output_file, voice, model, instructions=None, format="mp3", speed=1.0):
        """Generate speech and save to file"""
        if not self.client:
            logging.error("No API client available")
            raise ValueError("API client not initialized. Check API key.")
        
        # Remove asterisk if present
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
        
        try:
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
                return output_file
        except Exception as e:
            error_msg = f"Error generating speech: {str(e)}"
            logging.error(error_msg, exc_info=True)
            raise

    async def preview_audio_async(self, text, voice, model, instructions=None, speed=1.0):
        """Async function to preview audio"""
        if not self.async_client:
            logging.error("No async API client available")
            raise ValueError("Async API client not initialized. Check API key.")
        
        # Remove asterisk if present
        if " *" in voice:
            voice = voice.replace(" *", "")

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
        
        logging.info(f"Preview API call parameters: {json.dumps(api_params, indent=2)}")
        
        try:
            async with self.async_client.audio.speech.with_streaming_response.create(**api_params) as response:
                logging.info(f"Preview response received. Status: {response.status_code}")
                await LocalAudioPlayer().play(response)
                logging.info("Audio preview completed")
                return True
        except Exception as e:
            logging.error(f"Error in async audio preview: {str(e)}", exc_info=True)
            raise

    def preview_audio(self, text, voice, model, instructions=None, speed=1.0, callback=None):
        """Run the async preview in a separate thread"""
        def run_preview():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.preview_audio_async(text, voice, model, instructions, speed))
                loop.close()
                if callback:
                    callback(True, "")
            except Exception as e:
                error_msg = f"Error during audio preview: {str(e)}"
                logging.error(error_msg, exc_info=True)
                if callback:
                    callback(False, error_msg)
        
        # Start preview in a separate thread
        threading.Thread(target=run_preview, daemon=True).start()