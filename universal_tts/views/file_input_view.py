import tkinter as tk
from tkinter import ttk, scrolledtext

class FileInputView:
    """View for the file input tab"""
    
    def __init__(self, parent, browse_callback):
        self.parent = parent
        self.browse_callback = browse_callback
        self.frame = ttk.Frame(parent)
        
        # File path variable
        self.file_path_var = tk.StringVar()
        
        # Create the file input UI elements
        self.create_layout()
    
    def create_layout(self):
        """Create the layout for file input tab"""
        file_frame = ttk.Frame(self.frame)
        file_frame.pack(fill=tk.X, padx=5, pady=10)
        
        file_label = ttk.Label(file_frame, text="Select file (TXT, DOCX, PDF):")
        file_label.pack(side=tk.LEFT, padx=(0, 5))
        
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(file_frame, text="Browse", command=self.browse_callback)
        browse_button.pack(side=tk.RIGHT)
        
        preview_frame = ttk.LabelFrame(self.frame, text="File Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.file_preview = scrolledtext.ScrolledText(preview_frame, height=8)
        self.file_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def get_selected_file(self):
        """Get the selected file path"""
        return self.file_path_var.get() if self.file_path_var.get() else None
    
    def update_preview(self, text):
        """Update the file preview area with text"""
        self.file_preview.delete(1.0, tk.END)
        self.file_preview.insert(tk.END, text)