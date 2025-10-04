# -*- coding: utf-8 -*-

# Author: Yury
# Data: 04/10/2025

import os
import logging


def setup_logs(file: str) -> logging.Logger:
    """Sets up a unique logger for the current module, saving to logs/{file}
    
    Args:
        file (str): Log file name (e.g., 'scrapy_debug.txt')
    
    Returns:
        logging.Logger: Logger configured for the current module
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)


    logger_name = os.path.splitext(file)[0]
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(os.path.join(log_dir, file), mode="w")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger