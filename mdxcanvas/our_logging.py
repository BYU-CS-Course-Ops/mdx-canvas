import logging

logger: logging.Logger = None


def get_logger():
    global logger
    if logger is None:
        logger = logging.getLogger('MDXCANVAS')
        logger.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        # ch.setLevel(logging.INFO)

        format_tokens = [
            '%(asctime)s',
            # '%(name)s',
            '%(levelname)s',
            '%(message)s'
        ]
        formatter = logging.Formatter(' - '.join(format_tokens))
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger
