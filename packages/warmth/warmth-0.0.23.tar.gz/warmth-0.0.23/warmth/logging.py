import logging


def raise_exception_on_critical(record):
    if record.levelname == 'CRITICAL':
        raise Exception(f'{record.filename} {record.lineno} {record.msg}')
    return True


logger = logging.getLogger(__name__)
logger.addFilter(raise_exception_on_critical)
