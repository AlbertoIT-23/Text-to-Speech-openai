import os
import logging
from pathlib import Path
from dotenv import load_dotenv

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

class SettingsModel:
    """Model for managing API keys and application settings"""
    
    def __init__(self):
        self.api_key = self.get_api_key_from_sources()
        self.api_key_source = self._determine_api_key_source()
    
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
    
    def _determine_api_key_source(self):
        """Determine the source of the current API key"""
        if not self.api_key:
            return None
            
        # Check if key is in environment variables
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key == self.api_key:
            # Check if it's from .env file or session
            env_path = Path(".env")
            if env_path.exists():
                try:
                    with open(env_path, "r") as f:
                        if f"OPENAI_API_KEY={self.api_key}" in f.read():
                            return ".env file"
                except Exception:
                    pass
            return "current session only"
        
        # Check if key is in keyring
        if KEYRING_AVAILABLE:
            try:
                keyring_key = keyring.get_password(SERVICE_NAME, USERNAME)
                if keyring_key == self.api_key:
                    return "system credential manager"
            except Exception:
                pass
        
        return "unknown source"
    
    def save_api_key(self, key, storage_method):
        """Save API key with the selected storage method"""
        if not key:
            raise ValueError("API key cannot be empty")
        
        # Update for current session
        os.environ["OPENAI_API_KEY"] = key
        self.api_key = key
        
        # Store based on selected method
        if storage_method == "system" and KEYRING_AVAILABLE:
            try:
                keyring.set_password(SERVICE_NAME, USERNAME, key)
                self.api_key_source = "system credential manager"
                logging.info("API Key saved to system credential manager")
                return True
            except Exception as e:
                logging.error(f"Could not save to credential manager: {e}")
                raise
        
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
                
                self.api_key_source = ".env file"
                logging.info("API Key saved to .env file")
                return True
            except Exception as e:
                logging.error(f"Failed to update .env file: {e}")
                raise
        
        elif storage_method == "session":
            self.api_key_source = "current session only"
            logging.info("API Key updated for this session only")
            return True
        
        return False
    
    def delete_api_key(self):
        """Delete API key from all storage locations"""
        success_messages = []
        error_messages = []
        
        # 1. Remove from current session
        if self.api_key:
            self.api_key = None
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            success_messages.append("• Removed from current session")
            logging.info("API Key removed from current session")
        
        # 2. Remove from system credential manager
        if KEYRING_AVAILABLE:
            try:
                # keyring.delete_password raises an exception if key not found
                keyring.delete_password(SERVICE_NAME, USERNAME)
                success_messages.append("• Removed from system credential manager")
                logging.info("API Key removed from system credential manager")
            except Exception as e:
                # Log the error but continue
                logging.info(f"No API key found in system credential manager or error: {e}")
        
        # 3. Remove from .env file
        env_path = Path(".env")
        if env_path.exists():
            try:
                with open(env_path, "r") as f:
                    lines = f.readlines()
                
                # Remove any line starting with OPENAI_API_KEY
                new_lines = [line for line in lines if not line.startswith("OPENAI_API_KEY=")]
                
                # Write back to file if any lines were removed
                if len(new_lines) < len(lines):
                    with open(env_path, "w") as f:
                        f.writelines(new_lines)
                    success_messages.append("• Removed from .env file")
                    logging.info("API Key removed from .env file")
            except Exception as e:
                error_msg = f"Error removing API key from .env file: {e}"
                error_messages.append(f"• Failed to remove from .env file: {str(e)}")
                logging.error(error_msg)
        
        self.api_key_source = None
        
        return success_messages, error_messages
    
    def is_keyring_available(self):
        """Check if keyring is available"""
        return KEYRING_AVAILABLE