import tkinter as tk
from tkinter import scrolledtext, ttk

class TextInputView:
    """View for the text input tab"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        
        # Create the text input UI elements
        self.create_layout()
    
    def create_layout(self):
        """Create the layout for text input tab"""
        text_label = ttk.Label(self.frame, text="Enter or paste text:")
        text_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.text_input = scrolledtext.ScrolledText(self.frame, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_input.insert(tk.END, "Welcome to the Universal Text-to-Speech tool. This is a simple example of what you can create with OpenAI's speech synthesis API. You can customize the voice, tone, and style to suit your needs.")
    
    def get_text(self):
        """Get the text from the text input area"""
        text = self.text_input.get(1.0, tk.END).strip()
        return text if text else None