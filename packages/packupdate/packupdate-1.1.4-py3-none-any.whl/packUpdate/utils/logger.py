"""
Logging utilities for PackUpdate Python version
"""
import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, f"packupdate-{datetime.now().isoformat().replace(':', '-').replace('.', '-')}.log")
QUIET_MODE = False

def set_quiet_mode(quiet):
    """Set quiet mode for logging"""
    global QUIET_MODE
    QUIET_MODE = quiet

def write_log(message):
    """Write a message to the log file with timestamp."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def log(message):
    """Print message only if not in quiet mode."""
    if not QUIET_MODE:
        print(message)

def get_log_file():
    """Get current log file path"""
    return LOG_FILE

def get_log_dir():
    """Get log directory path"""
    return LOG_DIR
