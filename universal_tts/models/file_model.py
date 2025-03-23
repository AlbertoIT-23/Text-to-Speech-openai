import logging
from pathlib import Path
import datetime
from docx import Document
import fitz  # PyMuPDF

class FileModel:
    """Model for handling file operations"""
    
    def __init__(self):
        # Default output directory
        self.default_output_dir = str(Path("output"))
        self.supported_extensions = [".txt", ".docx", ".pdf"]
    
    def read_txt(self, file_path):
        """Read content from a text file"""
        logging.info(f"Reading TXT file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def read_docx(self, file_path):
        """Read content from a Word document"""
        logging.info(f"Reading DOCX file: {file_path}")
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    def read_pdf(self, file_path):
        """Read content from a PDF file"""
        logging.info(f"Reading PDF file: {file_path}")
        doc = fitz.open(file_path)
        return "\n".join([page.get_text() for page in doc])

    def read_file(self, file_path):
        """Read content from a file based on its extension"""
        file_path = Path(file_path)
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
    
    def ensure_output_directory(self, directory_path):
        """Ensure the output directory exists"""
        output_dir = Path(directory_path)
        output_dir.mkdir(exist_ok=True)
        return output_dir
    
    def generate_output_filename(self, input_filename=None, voice=None, format="mp3"):
        """Generate a unique output filename with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Remove asterisk if present in voice name for the filename
        if voice and " *" in voice:
            voice = voice.replace(" *", "")
        
        if input_filename:
            # Extract filename without extension
            base_name = Path(input_filename).stem
            return f"{base_name}_{voice}_{timestamp}.{format}"
        else:
            # Direct text input
            return f"speech_{voice}_{timestamp}.{format}"