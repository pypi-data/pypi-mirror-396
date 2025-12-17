import pybreaker
import requests

from .external_errors import NamedCircuitBreakerError


def call_with_breaker(breaker: pybreaker.CircuitBreaker, func):
    @breaker
    def wrapped():
        return func()
    return wrapped()

class NamedCircuitBreaker(pybreaker.CircuitBreaker):
    def __init__(self, name, fail_max=5, reset_timeout=60, success_threshold=1, **kwargs):

        # Function that identifies 4xx errors that should NOT count as failures
        def is_4xx_error(exception):
            if isinstance(exception, requests.exceptions.HTTPError):
                status_code = exception.response.status_code
                return 400 <= status_code < 500
            return False

        # Get existing exclude or create new one
        exclude = kwargs.get('exclude', []) or []
        if not isinstance(exclude, list):
            exclude = list(exclude)

        # Add function that excludes 4xx errors
        exclude.append(is_4xx_error)

        super().__init__(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            success_threshold=success_threshold,
            exclude=exclude,
            name=name,
            **kwargs
        )
        self._name = name

    def call(self, func, *args, **kwargs):
        if self._state.name == "open":
            raise NamedCircuitBreakerError(self._name)

        return super().call(func, *args, **kwargs)
