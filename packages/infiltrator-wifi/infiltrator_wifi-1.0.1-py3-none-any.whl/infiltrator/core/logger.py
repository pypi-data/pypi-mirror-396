"""Logging system for Infiltrator."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support."""
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}[{levelname}]{Style.RESET_ALL}"
        return super().format(record)

class Logger:
    """Manages logging for Infiltrator."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('Infiltrator')
        self.logger.setLevel(logging.DEBUG)
        
        log_dir = Path(config.get('output', 'logs_dir'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self._setup_handlers(log_dir)
    
    def _setup_handlers(self, log_dir: Path):
        self.logger.handlers.clear()
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter('%(levelname)s %(message)s')
        console_handler.setFormatter(console_formatter)
        
        log_file = log_dir / f"infiltrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def success(self, message: str):
        self.logger.info(f"{Fore.GREEN}[+] {message}{Style.RESET_ALL}")
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
