import os
import time
import logging
from pathlib import Path

def ensure_directory(directory_path):
    """Ensure a directory exists, creating it if necessary"""
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_unique_filename(directory, base_name, extension):
    """Generate a unique filename in the given directory"""
    counter = 0
    while True:
        if counter == 0:
            filename = f"{base_name}.{extension}"
        else:
            filename = f"{base_name}_{counter}.{extension}"
        
        file_path = Path(directory) / filename
        if not file_path.exists():
            return file_path
        counter += 1

def format_time_delta(seconds):
    """Format seconds into a human-readable time string"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def truncate_text(text, max_length=100, add_ellipsis=True):
    """Truncate text to a maximum length, optionally adding ellipsis"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    if add_ellipsis:
        truncated += "..."
    
    return truncated

def is_file_accessible(file_path, mode='r'):
    """Check if a file is accessible with the given mode"""
    try:
        with open(file_path, mode):
            return True
    except (IOError, PermissionError):
        return False