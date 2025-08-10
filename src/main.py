#!/usr/bin/env python3
"""
Boni AI - Main Application Entry Point
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.ai_engine import AIEngine
from utils.logger import setup_logger

def main():
    """Main application function"""
    logger = setup_logger()
    logger.info("Starting Boni AI...")
    
    try:
        # Initialize AI engine
        ai_engine = AIEngine()
        
        # Start the application
        ai_engine.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down Boni AI...")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
