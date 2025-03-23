import tkinter as tk
from tkinter import ttk, scrolledtext
from views.text_input_view import TextInputView
from views.file_input_view import FileInputView

class MainView:
    """Main application view with tabs and controls"""
    
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
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
        
        # Set style
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 11))
        self.style.configure('TLabel', font=('Arial', 11))
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready")
        
        # Create the main layout
        self.create_layout()
    
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
            command=self.controller.show_settings_dialog,
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
        
        # Create tabs for input methods
        self.tab_control = ttk.Notebook(self.scrollable_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create tab views
        self.text_input_view = TextInputView(self.tab_control)
        self.file_input_view = FileInputView(self.tab_control, self.controller.browse_file)
        
        # Add tabs
        self.tab_control.add(self.text_input_view.frame, text="Text Input")
        self.tab_control.add(self.file_input_view.frame, text="File Input")
        
        # Create voice options frame
        self.create_voice_options()
        
        # Create output options frame
        self.create_output_options()
        
        # Bottom controls in a fixed frame
        self.bottom_frame = ttk.Frame(self.root, padding="10")
        self.bottom_frame.grid(row=1, column=0, sticky="ew")

        # Configure columns for flexible layout
        self.bottom_frame.columnconfigure(0, weight=1)  
        self.bottom_frame.columnconfigure(1, weight=2)  
        self.bottom_frame.columnconfigure(2, weight=1)  

        # Status and buttons
        status_frame = ttk.Frame(self.bottom_frame)
        status_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

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
            command=self.controller.preview_audio,
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
            command=self.controller.generate_speech,
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
    
    def create_voice_options(self):
        """Create the voice options frame with controls"""
        # Voice options frame with grid layout
        voice_frame = ttk.LabelFrame(self.scrollable_frame, text="Voice Options", padding="10")
        voice_frame.pack(fill=tk.X, padx=5, pady=5)

        # Voice selection
        voice_label = ttk.Label(voice_frame, text="Voice:")
        voice_label.grid(row=0, column=0, sticky=tk.W, padx=(5, 0), pady=5)

        # Default voices
        default_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer", 
                          "ash *", "ballad *", "coral *", "sage *", "verse *"]
        
        self.voice_var = tk.StringVar(value="alloy")  # Default voice
        self.voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, 
                                           values=default_voices, width=15, state="readonly")
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
        self.model_dropdown = ttk.Combobox(voice_frame, textvariable=self.model_var, values=model_options, width=17, state="readonly")
        self.model_dropdown.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.model_dropdown.bind("<<ComboboxSelected>>", lambda e: self.controller.update_voice_options())

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
        
        self.instructions_text = tk.scrolledtext.ScrolledText(voice_frame, height=6, wrap=tk.WORD)
        self.instructions_text.grid(row=3, column=0, columnspan=8, sticky=tk.NSEW, padx=5, pady=5)
        self.instructions_text.insert(tk.END, "Speak clearly, with a warm and narrative tone.")

    def create_output_options(self):
            """Create the output options frame"""
            output_frame = ttk.LabelFrame(self.scrollable_frame, text="Output Options", padding="10")
            output_frame.pack(fill=tk.X, padx=5, pady=5)
            
            output_path_label = ttk.Label(output_frame, text="Output folder:")
            output_path_label.pack(side=tk.LEFT, padx=(0, 5))
            
            self.output_path_var = tk.StringVar(value="output")
            output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=40)
            output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            output_browse = ttk.Button(output_frame, text="Browse", command=self.controller.browse_output_folder)
            output_browse.pack(side=tk.LEFT, padx=(0, 5))
        
    def get_current_tab(self):
        """Get the currently selected tab index"""
        return self.tab_control.index(self.tab_control.select())
    
    def get_input_text(self):
        """Get text from the active input tab"""
        current_tab = self.get_current_tab()
        if current_tab == 0:  # Text input tab
            return self.text_input_view.get_text()
        else:  # File input tab
            return self.file_input_view.get_selected_file()
    
    def update_voice_options(self, available_voices):
        """Update voice dropdown with available voices for selected model"""
        # Create display options with asterisks for special voices
        display_options = []
        special_voices = ["ash", "ballad", "coral", "sage", "verse"]
        
        for voice in available_voices:
            if voice in special_voices:
                display_options.append(f"{voice} *")  # Add asterisk for special voices
            else:
                display_options.append(voice)
        
        # Update dropdown values
        self.voice_dropdown['values'] = display_options
    
    def start_progress(self, status_text="Processing..."):
        """Start the progress bar and update status"""
        self.status_var.set(status_text)
        self.progress_bar.start()
    
    def stop_progress(self, status_text="Ready"):
        """Stop the progress bar and update status"""
        self.progress_bar.stop()
        self.status_var.set(status_text)
    
    def show_success_dialog(self, output_file):
        """Show a success dialog with the output file path"""
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
        ttk.Label(frame, text=f"{output_file}", wraplength=430).pack(pady=(0, 8))  # Reduced padding and wrap width
        
        # OK button at the bottom with no extra space
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, expand=False, pady=(0, 0))  # No bottom padding
        
        # OK button centered
        ok_button = ttk.Button(button_frame, text="OK", command=info_dialog.destroy, width=8)
        ok_button.pack(pady=(20, 0))  # No padding
        
        # Center the dialog relative to the main window
        self.center_dialog(info_dialog)
    
    def center_dialog(self, dialog):
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