import logging
import os
import sys

# Setup library paths for shared objects
def setup_library_paths():
    """Add the prophecy package directory to library search paths"""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add to LD_LIBRARY_PATH for Linux
    if sys.platform.startswith('linux'):
        ld_library_path = os.environ.get('LD_LIBRARY_PATH', '')
        if package_dir not in ld_library_path:
            os.environ['LD_LIBRARY_PATH'] = f"{package_dir}:{ld_library_path}" if ld_library_path else package_dir
    
    # Add to DYLD_LIBRARY_PATH for macOS
    elif sys.platform == 'darwin':
        dyld_library_path = os.environ.get('DYLD_LIBRARY_PATH', '')
        if package_dir not in dyld_library_path:
            os.environ['DYLD_LIBRARY_PATH'] = f"{package_dir}:{dyld_library_path}" if dyld_library_path else package_dir

# Setup library paths before anything else
setup_library_paths()

def configure_logging():
    logger = logging.getLogger('python.sharedlib')

    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

configure_logging()

from .prophecy_api import (
    add_connection,
    get_connection,
    list_connections,
    load_connections_from_yaml,
    spark,
    read,
    write,
    close,
    reset,
    script_gem,
    instrument
)
from .prophecy_dataframe import ProphecyDataFrame
from . import secrets
from .secrets import ProphecySecrets, SecretsProvider

__all__ = [
    # DSL-style API (recommended)
    "read",
    "write",
    "spark",
    # Connection management
    "add_connection",
    "get_connection",
    "list_connections",
    "load_connections_from_yaml",
    "close",
    "reset",
    "script_gem",
    "instrument",
    # Data structures
    "ProphecyDataFrame",
    # Secrets management
    "secrets",
    "ProphecySecrets",
    "SecretsProvider",
]
__version__ = "1.0.19.dev1"

