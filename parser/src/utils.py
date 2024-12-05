import functools
import logging
import time

logger = logging.getLogger()


def retry(*exceptions, attempts: int, delay: int, backoff: int):
    def _retry_validator(_attempts: int):
        if _attempts <= 1:
            raise ValueError(
                "`attempts` should be > 1."
                "Passed {attempts}".format(attempts=_attempts)
            )

    _retry_validator(_attempts=attempts)

    def decorated(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _delay, _backoff = delay - backoff, backoff
            _attempts = attempts - 1

            for _ in range(_attempts):
                try:
                    result = func(*args, **kwargs)
                except exceptions as err:
                    logger.error(err)
                    logger.debug(kwargs)
                    _delay += _backoff
                    time.sleep(_delay)
                else:
                    return result
            return func(*args, **kwargs)

        return wrapper

    return decorated
