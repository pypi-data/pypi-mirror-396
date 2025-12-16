import logging
import os
from logging.handlers import RotatingFileHandler

from paper_inbox.modules.config.paths import get_log_dir


class PaddedFormatter(logging.Formatter):
    """
    A custom log formatter that aligns messages by padding the log prefix.
    """
    def __init__(self, fmt, *args, prefix_width=20, levelname_clip=0, **kwargs):
        super().__init__(fmt, *args, **kwargs)
        self.prefix_width = prefix_width
        self.levelname_clip = levelname_clip
        # Split the format string into a prefix and the message part
        if '%(message)s' in self._style._fmt:
            self.prefix_fmt = self._style._fmt.split('%(message)s', 1)[0]
        else:
            self.prefix_fmt = self._style._fmt

    def format(self, record):
        if self.levelname_clip > 0:
            record.levelname = record.levelname[:self.levelname_clip]
        return super().format(record)

    def formatMessage(self, record):
        # Format the prefix part of the log
        prefix = self.prefix_fmt % record.__dict__
        
        # Pad with spaces to ensure minimum width, then truncate to enforce maximum width.
        fixed_width_prefix = f"{prefix:<{self.prefix_width}}"[:self.prefix_width]
        
        # Return the fixed-width prefix along with the original message
        return f"{fixed_width_prefix} => {record.message}"

def get_global_log_level():
    log_level = os.getenv('LOG_LEVEL', None)
    if not log_level:
        log_level = logging.INFO
    return log_level

def setup_logger(name, level=None, verbose=False, silent_logging=False, add_date=True):
    ## in case we have set up a LOG_DIR env var we reroute
    ## the log file into there.
    log_filename = f"{name}.log"
    log_dir = get_log_dir()
    log_file = log_dir / log_filename

    ## get the logger instance
    logger = logging.getLogger(name)

    ## clear any existing handlers to prevent duplicate logging
    if logger.hasHandlers():
        logger.handlers.clear()

    ## set the logging level
    if not level:
        level = get_global_log_level()
    logger.setLevel(level)
    
    ## basic formatter string and settings 
    format_string = '[%(asctime)s: %(levelname)s/%(name)s] %(message)s'
    prefix_width = 26
    dateformat = '%H:%M:%S'
    if add_date:
        dateformat = '%Y-%m-%d %H:%M:%S'
    ## more detailed log output on verbose
    if verbose:
        format_string = '[%(asctime)s: %(levelname)s/%(name)s/%(filename)s:%(lineno)d] [%(processName)s] %(message)s'
        prefix_width = 70
        dateformat = None
    formatter = PaddedFormatter(format_string,
                                datefmt=dateformat,
                                levelname_clip=4,
                                prefix_width=prefix_width)
    
    ## setup file handler
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        delay=True
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    ## setup console handler (only if not silent)
    if not silent_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    ## prevent propagation to root logger
    logger.propagate = False
    
    return logger