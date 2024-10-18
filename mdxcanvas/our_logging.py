import logging

logger = None

def get_logger():
    global logger
    if logger is None:
        logger = logging.getLogger('MDXCANVAS')
        logger.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger