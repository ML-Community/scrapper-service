import time
from typing import Callable, Any


class RetryEntity:
    def __init__(self, func: Callable[[Any], Any], delay: int or float,
                 error: Exception, retry_amount: int) -> None:
        self.func = func
        self.delay = delay
        self.error = error
        self.retries = retry_amount

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, new_val: Exception) -> None:
        if issubclass(new_val, BaseException):
            self._error = new_val

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, new_val: Callable[[Any], Any]) -> None:
        if hasattr(new_val, "__call__"):
            self._func = new_val

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, new_val: int or float) -> None:
        if isinstance(new_val, (int, float)) and (0.1 <= new_val <= 5.0):
            self._delay = new_val

    @property
    def retries(self):
        return self._retries

    @retries.setter
    def retries(self, new_value: int) -> None:
        if (0 <= new_value <= 10) and isinstance(new_value, int):
            self._retries = new_value

    def decrease_retries(self):
        self.retries -= 1

    def retry_executing(self, *args: list):
        if self.retries == 0:
            raise Exception

        for _ in range(self.retries):
            try:
                return self.func(*args)
            except self.error:
                time.sleep(self.delay)
                self.decrease_retries()

    def __call__(self, *args, **kwargs):
        try:
            return self.retry_executing(*args)
        except self.error as task_err:
            print("Can't handle your function, ", task_err)
        except TypeError as err:
            print("Error with setting up attribute values, ", err)
        except Exception as err:
            print("Unexpected exception, ", err)

        return None


def retry(delay: int or float, error: Exception, retry_amount: int) -> Callable[[Any], Any]:
    def wrapper(func: Callable[[Any], Any]) -> RetryEntity:
        return RetryEntity(func, delay, error, retry_amount)
    return wrapper
