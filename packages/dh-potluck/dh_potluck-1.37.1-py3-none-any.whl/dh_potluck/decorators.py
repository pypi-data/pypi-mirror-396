import logging
import random
import time
from functools import wraps
from typing import Callable, ParamSpec, Type, TypeVar

module_logger = logging.getLogger(__name__)


P = ParamSpec('P')
R = TypeVar('R')


def retry(
    exceptions: Type[Exception] | tuple[Type[Exception], ...] = Exception,
    tries: int = 4,
    delay: float = 3,
    backoff: float = 2,
    custom_logger: logging.Logger | None = None,
    verbose: bool = False,
    skip_exceptions: bool = False,
    do_retry_func: Callable[[Exception], bool] | None = None,
    jitter: float = 0,
) -> Callable[[Callable[P, R]], Callable[P, R | None]]:
    """
    Retry calling the decorated function using an exponential backoff.

    :param exceptions: the exception to check. may be a tuple of exceptions to check
    :param tries: number of times to try (not retry) before giving up
    :param delay: initial delay between retries in seconds
    :param backoff: backoff multiplier e.g. value of 2 will double the delay each retry
    :param custom_logger: logger to use. If None, print
    :param verbose: Indicates if the stacktrace should be logged on the first retry
    :param skip_exceptions: Shows whether exceptions will be skipped or not after all tries
    :param do_retry_func: Function that determines if we should retry given the exception
    :param jitter: maximum jitter in seconds to apply to the wait time, introducing randomness.
    :return:
    """

    logger = custom_logger or module_logger

    if tries < 1:
        raise ValueError(f'`tries` must be >= 1, got {tries}')

    def deco_retry(f: Callable[P, R]) -> Callable[P, R | None]:
        @wraps(f)
        def f_retry(*args: P.args, **kwargs: P.kwargs) -> R | None:
            log_stacktrace = verbose
            wait_time = delay

            for remaining in range(tries - 1, -1, -1):
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    if _should_end_retrying(e, do_retry_func, remaining, logger):
                        if skip_exceptions:
                            return None
                        raise
                    logger.warning(
                        f'{e!r}, Retrying in {wait_time:.1f} seconds ... ({remaining=})',
                        exc_info=log_stacktrace,
                    )
                    time.sleep(wait_time)

                    wait_time = delay * backoff ** (tries - remaining) + random.uniform(0, jitter)
                    log_stacktrace = False

            raise AssertionError('unreachable')

        return f_retry

    return deco_retry


def _should_end_retrying(
    e: Exception,
    do_retry_func: Callable[[Exception], bool] | None,
    remaining: int,
    logger: logging.Logger,
):
    if do_retry_func and not do_retry_func(e):
        logger.info('No more retries')
        return True
    if not remaining:
        logger.warning('All retries exhausted, terminating.')
        return True
    return False
