import logging

logger: logging.Logger = None


def get_logger(course_name: str = None):
    global logger
    if logger is None:
        logger = logging.getLogger('MDXCANVAS')
        logger.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        # ch.setLevel(logging.INFO)

        format_tokens = [
            '%(asctime)s',
            # '%(name)s',
            *([course_name] if course_name is not None else []),
            '%(levelname)s',
            '%(message)s'
        ]
        formatter = logging.Formatter(' - '.join(format_tokens))
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger


def log_warnings(summary: list):
    for warning in summary:
        logger.warning(warning)
