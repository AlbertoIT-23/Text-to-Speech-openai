import tkinter as tk
from tkinter import ttk, messagebox

class SettingsView:
    """View for the settings dialog with API key management"""
    
    def __init__(self, parent, controller, api_key=None, api_key_source=None, keyring_available=True):
        self.parent = parent
        self.controller = controller
        self.api_key = api_key
        self.api_key_source = api_key_source
        self.keyring_available = keyring_available
        
        # Colors for styling
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
        
        # Create the dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Config API Key")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set dialog size
        self.dialog.geometry("450x410")
        self.dialog.minsize(450, 410)
        self.dialog.resizable(True, True)
        
        # Create dialog content
        self.create_dialog_content()
        
        # Center the dialog on the parent window
        self.center_dialog()
    
    def create_dialog_content(self):
        """Create the dialog content"""
        content_frame = ttk.Frame(self.dialog, padding="15")
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
        
        self.show_key_var = tk.BooleanVar(value=False)
        
        show_key_check = ttk.Checkbutton(
            key_entry_frame, 
            text="Show", 
            variable=self.show_key_var,
            command=self.toggle_key_visibility
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
        
        self.storage_var = tk.StringVar(value="system" if self.keyring_available else "env")
        
        system_radio = ttk.Radiobutton(
            storage_frame, 
            text="Store in system credential manager (recommended)", 
            variable=self.storage_var, 
            value="system"
        )
        system_radio.pack(anchor=tk.W, pady=1)
        
        env_radio = ttk.Radiobutton(
            storage_frame, 
            text="Store in .env file", 
            variable=self.storage_var, 
            value="env"
        )
        env_radio.pack(anchor=tk.W, pady=1)
        
        session_radio = ttk.Radiobutton(
            storage_frame, 
            text="Use for this session only", 
            variable=self.storage_var, 
            value="session"
        )
        session_radio.pack(anchor=tk.W, pady=1)
        
        # Disable system option if not available
        if not self.keyring_available:
            system_radio.config(state="disabled")
            key_note = ttk.Label(
                storage_frame, 
                text="System credential storage unavailable. Install 'keyring' package for enhanced security.", 
                font=('Segoe UI', 8, 'italic'),
                foreground=self.colors["text_secondary"]
            )
            key_note.pack(anchor=tk.W, pady=(3, 0))
        
        # Delete Key option
        delete_frame = ttk.LabelFrame(content_frame, text="Delete API Key", padding="8")
        delete_frame.pack(fill=tk.X, pady=(0, 10))
        
        delete_label = ttk.Label(
            delete_frame, 
            text="Remove the API key from all storage locations (system credential manager, .env file, and current session).",
            font=('Segoe UI', 9),
            wraplength=460
        )
        delete_label.pack(anchor=tk.W, pady=(0, 5))
        
        delete_button = tk.Button(
            delete_frame, 
            text="Delete API Key", 
            command=self.controller.delete_api_key,
            font=('Arial', 10),
            background="#dc3545", 
            foreground="white",
            activebackground="#c82333",
            relief=tk.RAISED,
            borderwidth=1,
            padx=8,
            pady=3,
            cursor="hand2"
        )
        delete_button.pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(8, 0))
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.dialog.destroy
        )
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_button = ttk.Button(
            button_frame, 
            text="Save API Key", 
            style="Primary.TButton",
            command=self.save_api_key
        )
        save_button.pack(side=tk.RIGHT)
    
    def toggle_key_visibility(self):
        """Toggle the visibility of the API key"""
        if self.show_key_var.get():
            self.api_entry.config(show="")
            if self.api_key and "•" in self.api_entry.get():
                # Replace masked key with actual key
                self.api_entry.delete(0, tk.END)
                self.api_entry.insert(0, self.api_key)
        else:
            self.api_entry.config(show="•")
    
    def save_api_key(self):
        """Save the API key with the selected storage method"""
        key = self.api_entry.get().strip()
        if not key:
            messagebox.showerror("Error", "Please enter a valid API Key", parent=self.dialog)
            return
        
        # Remove any placeholder chars if present
        if "•" in key:
            # User didn't change the masked display
            if self.api_key:
                # Keep using existing key
                key = self.api_key
            else:
                messagebox.showerror("Error", "Please enter a valid API Key", parent=self.dialog)
                return
        
        # Pass to controller for saving
        try:
            storage_method = self.storage_var.get()
            self.controller.save_api_key(key, storage_method)
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {str(e)}", parent=self.dialog)
    
    def center_dialog(self):
        """Center the dialog on its parent window"""
        self.dialog.update_idletasks()
        
        # Get parent and dialog dimensions
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Set position
        self.dialog.geometry(f"+{x}+{y}")
    
    def show_api_deletion_results(self, success_messages, error_messages):
        """Show the results of API key deletion"""
        if success_messages:
            success_text = "API Key successfully removed from:\n" + "\n".join(success_messages)
            if error_messages:
                success_text += "\n\nErrors encountered:\n" + "\n".join(error_messages)
            messagebox.showinfo("API Key Deleted", success_text, parent=self.dialog)
        elif error_messages:
            error_text = "Failed to remove API Key:\n" + "\n".join(error_messages)
            messagebox.showerror("Error", error_text, parent=self.dialog)
        else:
            messagebox.showinfo("No Action Needed", "No API Key was found to delete.", parent=self.dialog)