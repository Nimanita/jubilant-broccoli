import logging
from datetime import datetime
import os
from functools import wraps

def setup_logger():
    """Setup application logger"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()  # Console output
        ]
    )
    
    return logging.getLogger(__name__)

# Fixed request logger decorator
def log_request(func):
    """Decorator to log API requests"""
    @wraps(func)  # This preserves the original function name
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.info(f"Request: {func.__name__} - {datetime.now()}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Success: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper