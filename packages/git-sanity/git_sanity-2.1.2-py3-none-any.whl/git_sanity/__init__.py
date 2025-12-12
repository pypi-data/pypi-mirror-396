import logging

__prog_name__ = "git-sanity"
__version__ = "2.1.2"
__author__ = "yuqiaoyu"
__config_root_dir__ = f".{__prog_name__}"
__config_file_name__ = f"{__prog_name__}_config.json"
__prog_log_file_name__ = f"{__prog_name__}.log"

class ColorFormatter(logging.Formatter):
    grey = "\033[90m"
    green = "\033[32m"
    yellow = "\033[33m"
    red = "\033[31m"
    bold_red = "\033[31;41m"
    reset = "\033[0m"
    log_format = f"%(asctime)s {__prog_name__} %(levelname)s %(filename)s:%(lineno)d: %(message)s"
    FORMATS = {
        logging.DEBUG: grey + log_format + reset,
        logging.INFO: log_format,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset,
    }
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColorFormatter())
if not logger.handlers:
    logger.addHandler(console_handler)