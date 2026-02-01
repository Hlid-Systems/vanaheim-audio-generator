import logging
import sys
import os

# Check if colorlog is installed (it's nice but optional, falling back if not)
try:
    import colorlog
except ImportError:
    colorlog = None

def setup_logging():
    """
    Configures the application logger with console (colored) and file handlers.
    """
    logger = logging.getLogger("vanaheim_audio")
    logger.setLevel(logging.INFO)
    logger.propagate = False # Prevent double logging if attached to root

    # 1. Console Handler (Visual/Emoji)
    console_handler = logging.StreamHandler(sys.stdout)
    
    if colorlog:
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_purple',
            }
        )
    else:
        # Fallback formatter with emojis
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    
    # 2. File Handler (Persistent Trace)
    # The code automatically creates this directory.
    log_dir = "logs" 
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, "vanaheim.log"), encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
    return logger

logger = setup_logging()