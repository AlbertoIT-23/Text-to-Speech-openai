import os
import logging
import datetime
from pathlib import Path

def setup_logging():
    """Setup logging to file with enhanced error checking"""
    try:
        # Reset any existing logger configuration first
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        try:
            logs_dir.mkdir(exist_ok=True)
            print(f"Logs directory: {logs_dir.absolute()} {'exists' if logs_dir.exists() else 'creation failed'}")
        except Exception as dir_err:
            print(f"Error creating logs directory: {dir_err}")
            logs_dir = Path(".")
        
        # Create a log file with timestamp in name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"tts_log_{timestamp}.log"
        
        print(f"Attempting to create log file: {log_file.absolute()}")
        
        # Test if we can write to the file
        try:
            with open(log_file, 'w') as f:
                f.write(f"Log started at {datetime.datetime.now().isoformat()}\n")
            print(f"Log file created successfully: {log_file}")
        except Exception as file_err:
            print(f"Cannot write to log file: {file_err}")
            log_file = Path(f"./tts_log_{timestamp}.log")
            try:
                with open(log_file, 'w') as f:
                    f.write(f"Log started at {datetime.datetime.now().isoformat()}\n")
                print(f"Created fallback log file: {log_file}")
            except Exception as fallback_err:
                print(f"Cannot create fallback log file: {fallback_err}")
                return False
        
        # Configure basic logging
        logging.basicConfig(
            filename=str(log_file),
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filemode='w'  # Overwrite if exists
        )
        
        # Add console handler for informational messages
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        
        # Make sure we don't add duplicate handlers
        root_logger = logging.getLogger('')
        has_console = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
        if not has_console:
            root_logger.addHandler(console)
            
        # Log startup information
        logging.info(f"Logging initialized to: {log_file}")
        logging.info(f"Application started at: {datetime.datetime.now().isoformat()}")
        logging.info(f"Python version: {os.sys.version}")
        logging.info(f"Operating system: {os.name} - {os.sys.platform}")
        
        print(f"Logging to: {log_file}")
        return True
        
    except Exception as e:
        print(f"Critical error in setup_logging: {e}")
        # Fallback to console-only logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        print("Fallback to console logging only")
        return False