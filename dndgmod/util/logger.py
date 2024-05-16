import enum
import logging

LOG_LEVEL_MAPPING = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

class LogLevels(enum.Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"


def logger_setup(ctx, log_level):
    logger = logging.getLogger("dndgmod")
    logger.setLevel(LOG_LEVEL_MAPPING[log_level.value])
    logger.addHandler(logging.StreamHandler())
    ctx.obj["logger"] = logger
