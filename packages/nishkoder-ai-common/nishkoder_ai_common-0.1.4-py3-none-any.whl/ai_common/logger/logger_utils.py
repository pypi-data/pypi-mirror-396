import logging
from typing import Any, Dict

class ContextAdapter(logging.LoggerAdapter):
    """LoggerAdapter that adds contextual information to log records.

    Usage:
        logger = get_logger()
        adapter = add_context(logger, request_id='abc123', user_id='user42')
        adapter.info('User request processed')
    """
    def process(self, msg: str, kwargs: Dict[str, Any]):
        # Merge extra dict with existing extra if present
        extra = self.extra.copy()
        if 'extra' in kwargs:
            extra.update(kwargs['extra'])
        kwargs['extra'] = extra
        return msg, kwargs

def add_context(logger: logging.Logger, **extra) -> ContextAdapter:
    """Return a LoggerAdapter that injects the provided extra context into log records.

    Parameters
    ----------
    logger: logging.Logger
        The base logger to wrap.
    **extra: dict
        Arbitrary key/value pairs that will be added to each log record.
    """
    return ContextAdapter(logger, extra)
