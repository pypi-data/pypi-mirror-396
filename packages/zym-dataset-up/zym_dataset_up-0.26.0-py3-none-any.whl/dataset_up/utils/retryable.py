import time
import requests
from dataset_up.log.logger import get_logger

logger = get_logger(__name__)

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retry_count = 0
            delay = base_delay
            exception = None
            while retry_count < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    exception = e
                    if isinstance(e, requests.exceptions.RequestException):
                        if str(e).__contains__("Unauthorized"):
                            logger.critical(f"{e}")
                            break
                        logger.error(f"RequestException happend when {func.__name__} ,msg: {e}")
                    if isinstance(e, requests.exceptions.ConnectionError):
                        logger.error(f"ConnectionError happend when {func.__name__} ,msg: {e}")
                         
                    elif isinstance(e, requests.exceptions.Timeout):
                        logger.error(f"Timeout happend when {func.__name__} ,msg: {e}")
                        
                    elif isinstance(e, requests.exceptions.HTTPError):
                        logger.error(f"HTTPError happend when {func.__name__} ,msg: {e}")
                        
                    else:
                        if str(e).__contains__("Access Denied"):
                            logger.critical(f"{e}")
                            break
                        logger.error(f"Unexpected error happend when {func.__name__},msg: {e}")
    
                    time.sleep(delay)
                    retry_count += 1
                    delay = min(delay * 1.5, max_delay)
                    
            raise Exception(
                f"function {func.__name__} failed after {retry_count} retries,msg:{exception}"
            )
        return wrapper
    return decorator