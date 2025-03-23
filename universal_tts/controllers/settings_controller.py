import logging
import tkinter as tk
from tkinter import messagebox
from views.settings_view import SettingsView

class SettingsController:
    """Controller for the settings dialog"""
    
    def __init__(self, parent, settings_model, tts_model):
        self.parent = parent
        self.settings_model = settings_model
        self.tts_model = tts_model
        self.view = None
    
    def show_dialog(self):
        """Show the settings dialog"""
        self.view = SettingsView(
            self.parent,
            self,
            api_key=self.settings_model.api_key,
            api_key_source=self.settings_model.api_key_source,
            keyring_available=self.settings_model.is_keyring_available()
        )
    
    def save_api_key(self, key, storage_method):
        """Save the API key with the selected storage method"""
        logging.info(f"Saving API key using storage method: {storage_method}")
        try:
            # Save in settings model
            self.settings_model.save_api_key(key, storage_method)
            
            # Update TTS model with the new key
            self.tts_model.set_api_key(key)
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                f"API Key saved {storage_method if storage_method == 'session' else 'to ' + storage_method}", 
                parent=self.view.dialog
            )
            
            return True
        except Exception as e:
            logging.error(f"Error saving API key: {e}", exc_info=True)
            messagebox.showerror(
                "Error", 
                f"Failed to save API key: {str(e)}", 
                parent=self.view.dialog
            )
            return False
    
    def delete_api_key(self):
        """Delete the API key from all storage locations"""
        # Confirm with user before deleting
        if not messagebox.askyesno(
            "Confirm Deletion", 
            "Are you sure you want to delete your OpenAI API key from all storage locations?\n\n"
            "This will remove the key from:\n"
            "• System credential manager (if used)\n"
            "• .env file (if present)\n"
            "• Current session\n\n"
            "You'll need to enter your API key again to use the application.",
            icon=messagebox.WARNING,
            parent=self.view.dialog
        ):
            return  # User cancelled
        
        # Delete the key
        success_messages, error_messages = self.settings_model.delete_api_key()
        
        # Clear the API key entry field
        self.view.api_entry.delete(0, tk.END)
        
        # Update TTS model
        self.tts_model.set_api_key(None)
        
        # Show results
        self.view.show_api_deletion_results(success_messages, error_messages)