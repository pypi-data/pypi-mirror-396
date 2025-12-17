"""
🏥 Oumi Hospital - Logging Configuration

Setup logging compatible with Oumi's native logging format for seamless integration.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

# Hospital-themed console for logging
log_console = Console(stderr=True, width=120)

class HospitalFormatter(logging.Formatter):
    """Custom formatter with hospital theme and Oumi compatibility"""
    
    def __init__(self):
        # Format compatible with Oumi's logging style
        super().__init__(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    def format(self, record):
        # Add hospital context to log records
        if not hasattr(record, 'hospital_agent'):
            record.hospital_agent = "system"
        
        # Color code by level (for file logs)
        level_colors = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        
        record.level_emoji = level_colors.get(record.levelname, 'ℹ️')
        
        # Format with emoji prefix
        formatted = super().format(record)
        return f"{record.level_emoji} {formatted}"


def setup_hospital_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_rich: bool = True
) -> logging.Logger:
    """
    Setup logging for Oumi Hospital with Rich console output and file logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        enable_rich: Whether to use Rich console handler
    
    Returns:
        Configured logger instance
    """
    
    # Create main logger
    logger = logging.getLogger("oumi_hospital")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Rich console handler for beautiful terminal output
    if enable_rich:
        rich_handler = RichHandler(
            console=log_console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )
        rich_handler.setLevel(getattr(logging, log_level.upper()))
        logger.addHandler(rich_handler)
    
    # File handler for persistent logs
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        file_handler.setFormatter(HospitalFormatter())
        logger.addHandler(file_handler)
    
    # Also setup Oumi's loggers to match our format
    setup_oumi_logging_compatibility(log_level)
    
    logger.info("🏥 Hospital logging initialized")
    logger.info(f"📊 Log level: {log_level}")
    if log_file:
        logger.info(f"📁 Log file: {log_file}")
    
    return logger


def setup_oumi_logging_compatibility(log_level: str = "INFO"):
    """Setup Oumi's internal loggers to match our format"""
    
    # Common Oumi logger names (based on documentation)
    oumi_loggers = [
        "oumi",
        "oumi.core",
        "oumi.inference", 
        "oumi.evaluation",
        "oumi.training",
        "transformers",
        "datasets",
        "torch"
    ]
    
    for logger_name in oumi_loggers:
        oumi_logger = logging.getLogger(logger_name)
        
        # Set appropriate levels
        if logger_name in ["transformers", "datasets", "torch"]:
            # Reduce noise from dependencies
            oumi_logger.setLevel(logging.WARNING)
        else:
            oumi_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate logs
        oumi_logger.propagate = True


def get_hospital_logger(name: str) -> logging.Logger:
    """Get a logger for a specific hospital component"""
    return logging.getLogger(f"oumi_hospital.{name}")


def log_agent_action(logger: logging.Logger, agent: str, action: str, details: str = ""):
    """Log an agent action with consistent formatting"""
    extra = {"hospital_agent": agent}
    
    agent_emojis = {
        "diagnostician": "🔍",
        "pharmacist": "💊", 
        "neurologist": "🧠",
        "surgeon": "🔧"
    }
    
    emoji = agent_emojis.get(agent.lower(), "🏥")
    message = f"{emoji} {agent.title()}: {action}"
    
    if details:
        message += f" - {details}"
    
    logger.info(message, extra=extra)


def log_oumi_api_call(logger: logging.Logger, api: str, model: str, details: str = ""):
    """Log Oumi API calls for debugging"""
    message = f"🔗 Oumi API: {api} with {model}"
    if details:
        message += f" - {details}"
    
    logger.debug(message)


def log_performance_metric(logger: logging.Logger, metric: str, value: float, unit: str = ""):
    """Log performance metrics"""
    message = f"📊 Performance: {metric} = {value:.3f}"
    if unit:
        message += f" {unit}"
    
    logger.info(message)


def create_session_log_file() -> str:
    """Create a unique log file for this session"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return str(log_dir / f"hospital_session_{timestamp}.log")


# Default logger setup
def get_default_logger() -> logging.Logger:
    """Get the default hospital logger with standard configuration"""
    return setup_hospital_logging(
        log_level="INFO",
        log_file=create_session_log_file(),
        enable_rich=True
    )


# Context manager for agent logging
class AgentLogContext:
    """Context manager for agent-specific logging"""
    
    def __init__(self, agent_name: str, action: str):
        self.agent_name = agent_name
        self.action = action
        self.logger = get_hospital_logger(agent_name)
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        log_agent_action(self.logger, self.agent_name, f"Starting {self.action}")
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            log_agent_action(
                self.logger, 
                self.agent_name, 
                f"Completed {self.action}",
                f"Duration: {duration:.2f}s"
            )
        else:
            log_agent_action(
                self.logger,
                self.agent_name, 
                f"Failed {self.action}",
                f"Error: {exc_val}"
            )


__all__ = [
    "setup_hospital_logging",
    "get_hospital_logger", 
    "log_agent_action",
    "log_oumi_api_call",
    "log_performance_metric",
    "create_session_log_file",
    "get_default_logger",
    "AgentLogContext",
    "HospitalFormatter"
]