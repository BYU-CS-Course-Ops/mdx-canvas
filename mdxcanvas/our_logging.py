import logging

logger = None

def get_logger(name: str = None):
    global logger
    if logger is None:
        logger = logging.getLogger('MDXCANVAS')
        logger.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)
    if name:
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                formatter = logging.Formatter(f'%(asctime)s - {name} - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                break

    return logger
