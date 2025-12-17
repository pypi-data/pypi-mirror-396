"""
Logging configuration for the Holos SDK.

This module provides simple console logging setup with thread ID filtering.
"""

import logging
import threading

def thread_id_filter(record):
    """Inject thread_id to log records"""
    record.thread_id = threading.get_ident() % 100000
    return record


def setup_logging(level=logging.INFO):
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.addFilter(thread_id_filter)
    
    # Set formatter
    formatter = logging.Formatter(
        "%(asctime)s %(thread_id)d %(name)s:%(lineno)d [%(levelname)s] %(message)s"
    )
    console_handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=level,
        handlers=[console_handler]
    )
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
