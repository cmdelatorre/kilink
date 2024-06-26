"""Kilink main module."""

import logging
import os
import sys
import threading
import traceback

from logging.handlers import TimedRotatingFileHandler as TRFHandler

from kilink.config import config, ENVIRONMENT_KEY, PROD_ENVIRONMENT_VALUE

log_setup_lock = threading.Lock()


def exception_handler(exc_type, exc_value, tb):
    """Handle an unhandled exception."""
    exception = traceback.format_exception(exc_type, exc_value, tb)
    msg = "".join(exception)
    print(msg, file=sys.stderr)

    # log
    logger = logging.getLogger('kilink')
    logger.error("Unhandled exception!\n%s", msg)


def _setup(logdir, verbose):
    """Really do the setup, but not threading safe."""
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    logger = logging.getLogger('kilink')
    fname = os.path.join(logdir, 'linkode.log')
    handler = TRFHandler(fname, when='D', interval=1)
    logger.addHandler(handler)
    formatter = logging.Formatter("%(asctime)s  %(name)-22s  "
                                  "%(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)

    if verbose:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)

    # hook the exception handler
    sys.excepthook = exception_handler


def setup_logging(_logger, verbose=False):
    """Set up the logging.

    This is thread-safe; it will only call the setup if logger doesn't have
    handlers already set.
    """
    logdir = config['log_directory']

    with log_setup_lock:
        kilink_logger = logging.getLogger('kilink')
        if not kilink_logger.handlers:
            _setup(logdir, verbose)

    for h in kilink_logger.handlers:
        if config[ENVIRONMENT_KEY] != PROD_ENVIRONMENT_VALUE:
            h.setLevel(logging.DEBUG)
        _logger.addHandler(h)

    if config[ENVIRONMENT_KEY] != PROD_ENVIRONMENT_VALUE:
        _logger.setLevel(logging.DEBUG)
