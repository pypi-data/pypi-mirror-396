#!/usr/bin/env python3
"""
Main CLI entry point for Infiltrator.
This is the console script that gets installed with the package.
"""

import sys
import os
from pathlib import Path

def check_root():
    """Check if running with root privileges."""
    if os.name == 'posix':
        if os.geteuid() != 0:
            print("\n❌ ERROR: Infiltrator requires root privileges!")
            print("Please run with: sudo infiltrator")
            print("Or: sudo python3 -m infiltrator")
            sys.exit(1)

def main():
    """Main entry point for the infiltrator command."""
    from infiltrator.core.banner import display_banner
    from infiltrator.core.config import Config
    from infiltrator.core.logger import Logger
    from infiltrator.core.menu import CLI
    
    # Display banner
    display_banner()
    
    # Check privileges
    check_root()
    
    # Initialize configuration
    config = Config()
    
    # Initialize logger
    logger = Logger(config)
    
    # Initialize and run CLI
    try:
        cli = CLI(config, logger)
        cli.run()
    except KeyboardInterrupt:
        logger.info("\n[!] Interrupted by user. Cleaning up...")
        if 'cli' in locals():
            cli.cleanup()
        sys.exit(0)
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"Fatal error: {e}")
        else:
            print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
