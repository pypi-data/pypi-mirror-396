"""
Tubox Client Configuration - Production-ready settings.

This module provides configuration options for the Tubox API Client,
allowing fine-tuning of connection pooling, timeouts, retries, and logging.

Usage:
    from tubox_client.config import ClientConfig
    
    config = ClientConfig(
        host="tubox.example.com",
        port=7188,
        max_connections=50,
        request_timeout=60.0,
        retry_max_attempts=5
    )
    
    client = TuboxClient(
        host=config.host,
        port=config.port,
        max_pool_size=config.max_pool_size,
        max_connections=config.max_connections
    )
"""

import os
from typing import Optional
import logging


class ClientConfig:
    """Production-ready client configuration."""
    
    # Connection settings
    HOST: str = os.getenv("TUBOX_HOST", "localhost")
    PORT: int = int(os.getenv("TUBOX_PORT", "7188"))
    
    # Connection pooling
    MIN_POOL_SIZE: int = 1
    MAX_POOL_SIZE: int = 10
    MAX_CONNECTIONS: int = 100
    CONNECTION_REUSE_TIMEOUT: float = 300.0  # 5 minutes
    
    # Timeouts (seconds)
    CONNECT_TIMEOUT: float = 10.0
    REQUEST_TIMEOUT: float = 30.0
    POOL_TIMEOUT: float = 5.0
    
    # Retry settings
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_INITIAL_DELAY: float = 0.1  # 100ms
    RETRY_MAX_DELAY: float = 10.0  # 10 seconds
    RETRY_BACKOFF_FACTOR: float = 2.0
    
    # Logging
    LOG_LEVEL: str = os.getenv("TUBOX_LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        max_pool_size: Optional[int] = None,
        max_connections: Optional[int] = None,
        connect_timeout: Optional[float] = None,
        request_timeout: Optional[float] = None,
        retry_max_attempts: Optional[int] = None,
        log_level: Optional[str] = None,
    ):
        """Initialize configuration with optional overrides."""
        self.host = host or self.HOST
        self.port = port or self.PORT
        self.max_pool_size = max_pool_size or self.MAX_POOL_SIZE
        self.max_connections = max_connections or self.MAX_CONNECTIONS
        self.connect_timeout = connect_timeout or self.CONNECT_TIMEOUT
        self.request_timeout = request_timeout or self.REQUEST_TIMEOUT
        self.retry_max_attempts = retry_max_attempts or self.RETRY_MAX_ATTEMPTS
        self.log_level = log_level or self.LOG_LEVEL
    
    def configure_logging(self, logger_name: str = "tubox.client"):
        """Configure logging for Tubox client."""
        logger = logging.getLogger(logger_name)
        
        # Only configure if not already configured
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.LOG_FORMAT)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(self.log_level)
        
        return logger
    
    def to_dict(self) -> dict:
        """Export configuration as dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "max_pool_size": self.max_pool_size,
            "max_connections": self.max_connections,
            "connect_timeout": self.connect_timeout,
            "request_timeout": self.request_timeout,
            "retry_max_attempts": self.retry_max_attempts,
            "log_level": self.log_level,
        }
    
    def __repr__(self):
        return f"ClientConfig({self.to_dict()})"


# Default configuration instance
default_config = ClientConfig()
