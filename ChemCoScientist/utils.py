import time
import logging
from functools import wraps

import logging
from logging.handlers import RotatingFileHandler

def setup_logger(
    log_file: str = "timing.log",
    level: int = logging.INFO
):
    logger = logging.getLogger("timing_logger")
    logger.setLevel(level)

    handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger

logger = setup_logger()


def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start

        if  func.__name__ not in {'retrieve_semantic_context', 'get_embeddings', 'resolve_message'}:
            context = args[0]
            fin_res = result
        elif func.__name__  == 'resolve_message':
            context = kwargs
            fin_res = result
        else:
            context = fin_res = None
            
        logger.info(
            f"Function {func.__name__} executed in {elapsed} seconds with input:\n {context}\n and result:\n {fin_res}"
        )

        return result
    return wrapper
