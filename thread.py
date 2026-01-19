import threading
from typing import Any, Callable, Mapping, Iterable


class ThreadWithResult(threading.Thread):

    _result: Any
    _exception: BaseException | None

    def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = (), kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self._result = None
        self._exception = None

    def run(self):
        try:
            self._result = self._target(*self._args, **self._kwargs)  # type: ignore
        except Exception as e:
            self._exception = e

    def result(self, timeout=None):
        self.join(timeout)
        if self.is_alive():
            raise TimeoutError("Thread did not complete within timeout")
        if self._exception:
            # Re-raise the exception from the thread context
            raise self._exception
        return self._result