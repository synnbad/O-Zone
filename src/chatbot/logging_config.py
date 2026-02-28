"""
Logging Configuration for O-Zone Chatbot

Provides centralized logging setup for all chatbot components.
"""

import logging
import logging.handlers
import os
from pathlib import Path


def setup_chatbot_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """
    Configures logging for chatbot components.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler (max 10MB, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure chatbot component loggers
    chatbot_loggers = [
        'src.chatbot.session_manager',
        'src.chatbot.user_profiler',
        'src.chatbot.conversation_manager',
        'src.chatbot.response_generator',
        'src.chatbot.bedrock_adapter',
        'src.chatbot.backend_integration',
        'src.chatbot.chatbot_interface',
    ]
    
    for logger_name in chatbot_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
    
    # Log startup message
    logging.info("Chatbot logging configured successfully")


def get_log_level_from_env() -> str:
    """
    Gets log level from environment variable.
    
    Returns:
        Log level string (defaults to INFO)
    """
    return os.getenv("CHATBOT_LOG_LEVEL", "INFO").upper()


def get_log_file_from_env() -> str:
    """
    Gets log file path from environment variable.
    
    Returns:
        Log file path or None
    """
    return os.getenv("CHATBOT_LOG_FILE")
