import logging
import os
from pathlib import Path

import arrow as ar
import logzero


def read_config(path_config_file):
    """

    Args:
        path_config_file ():

    Returns:

    """
    from configparser import ConfigParser, ExtendedInterpolation

    parser = ConfigParser(
        inline_comment_prefixes=(";",), interpolation=ExtendedInterpolation()
    )

    try:
        parser.read(path_config_file)
    except Exception as e:
        raise IOError(f"Cannot read {path_config_file}: {e}")

    return parser


class Logger:
    # adapted from https://gist.github.com/empr/2036153
    # Level	    Numeric value
    # CRITICAL	      50
    # ERROR	          40
    # WARNING	      30
    # INFO	          20
    # DEBUG	          10
    # NOTSET	       0
    def __init__(
        self,
        dir_log,  # Path to the directory where the log file will be saved
        project="geoprepare",  # Name of the project, this will be created as a subdirectory in dir_log
        file="logger.txt",  # Name of the log file
        level=logging.INFO,  # Logging level (see above)
    ):
        log_format = "[%(asctime)s] %(message)s"
        dir_log = Path(dir_log) / project / ar.now().format("MMMM_DD_YYYY")
        os.makedirs(dir_log, exist_ok=True)

        self.logger = logzero.setup_logger(
            name=file,
            logfile=dir_log / file,
            formatter=logzero.LogFormatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M"),
            maxBytes=int(1e6),  # 1 MB size
            backupCount=3,
            level=level,
        )

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)


def get_logging_level(level):
    """

    Args:
        level:

    Returns:

    """
    if level == "DEBUG":
        return logging.DEBUG
    elif level == "INFO":
        return logging.INFO
    elif level == "WARNING":
        return logging.WARNING
    elif level == "ERROR":
        return logging.ERROR
    else:
        return logging.INFO


def setup_logger_parser(path_config_file, name_project="geocif", name_file="ml"):
    """

    Args:
        path_config_file:
        name_project:
        name_file:
        level:

    Returns:

    """
    parser = read_config(path_config_file)
    dir_log = parser.get("PATHS", "dir_log")
    level = parser.get("LOGGING", "log_level")
    level = get_logging_level(level)

    logger = Logger(
        dir_log=dir_log,
        project=name_project,
        file=name_file,
        level=level,
    )

    return logger, parser
