import logging.config
import os.path

__Basic_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'tmp.log',
            'maxBytes': 10*1024*1024,  # 10 MB
            'backupCount': 3,
            'encoding': 'utf8',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default', "console"],
            'level': 'INFO',
            'propagate': True
        },
    }
}


def init_logging(log_file: str = "tmp.log", level: str = "INFO") -> None:
    log_dir = os.path.dirname(log_file)
    if os.path.exists(log_dir) is False:
        os.makedirs(log_dir)
    _basic = __Basic_CONFIG
    _basic["handlers"]["default"]["filename"] = log_file
    _basic["loggers"][""]["level"] = level
    logging.config.dictConfig(__Basic_CONFIG)