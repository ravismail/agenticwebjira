import logging
import sys

def setup_logging():
    """Sets up logging to stdout with a standard format."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Ensure standard prints are also flushed/visible if possible
    # but primarily encourage using logger

def get_logger(name):
    return logging.getLogger(name)
