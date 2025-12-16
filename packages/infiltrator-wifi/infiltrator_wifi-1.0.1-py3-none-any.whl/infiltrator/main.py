#!/usr/bin/env python3
"""
Infiltrator Wi-Fi Auditing Suite
Dev: LAKSHMIKANTHAN K (letchupkt)

Main entry point for the Infiltrator framework.
"""

import sys
import os
from pathlib import Path

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent / 'core'))
sys.path.insert(0, str(Path(__file__).parent / 'modules'))

from core.cli import CLI
from core.banner import display_banner
from core.config import Config
from core.logger import Logger

def main():
    """Main entry point for Infiltrator."""
    # Display banner
    display_banner()
    
    # Initialize configuration
    config = Config()
    
    # Initialize logger
    logger = Logger(config)
    
    # Check for root/admin privileges
    if os.geteuid() != 0 if hasattr(os, 'geteuid') else True:
        logger.error("Infiltrator requires root/administrator privileges!")
        logger.warning("Please run with: sudo python3 infiltrator.py")
        sys.exit(1)
    
    # Initialize and run CLI
    try:
        cli = CLI(config, logger)
        cli.run()
    except KeyboardInterrupt:
        logger.info("\n[!] Interrupted by user. Cleaning up...")
        cli.cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
