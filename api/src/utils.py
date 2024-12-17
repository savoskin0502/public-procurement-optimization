import asyncio
import functools
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


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
        async def wrapper(*args, **kwargs):
            _delay, _backoff = delay - backoff, backoff
            _attempts = attempts - 1

            for _ in range(_attempts):
                try:
                    result = await func(*args, **kwargs)
                except exceptions as err:
                    logger.debug(err)
                    logger.debug(type(err))
                    logger.debug(kwargs)
                    _delay += _backoff
                    await asyncio.sleep(_delay)
                else:
                    return result
            return await func(*args, **kwargs)

        return wrapper

    return decorated
