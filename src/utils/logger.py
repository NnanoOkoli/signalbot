"""
Boni AI - Logging Utilities
"""

import sys
from loguru import logger

def setup_logger(level: str = "INFO") -> logger:
    """Setup and configure logger"""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # Add file handler
    logger.add(
        "logs/boni_ai.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation="1 day",
        retention="7 days"
    )
    
    return logger
