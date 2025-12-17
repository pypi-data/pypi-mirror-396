from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar

from static_error_handler import Err, Ok, Result

T = TypeVar("T")
E = TypeVar("E")
R = TypeVar("R")


def process_results(
    iterable: Iterable[Result[T, E]], func: Callable[[Iterable[T]], R]
) -> Result[R, E]:
    """
    Adapt an iterable of Result[T, E] into an iterable of T.

    - If all items are Ok, returns Ok(func(values)).
    - If any Err is encountered, iteration stops early and returns that Err.
    """
    sentinel = object()
    captured: E | object = sentinel

    def result_unwrapper() -> Iterator[T]:
        nonlocal captured
        for item in iterable:
            if item.is_ok():
                yield item.unwrap()
            else:
                captured = item.unwrap_err()
                return

    computed_value = func(result_unwrapper())

    if captured is not sentinel:
        return Err(captured)  # type: ignore[arg-type]

    return Ok(computed_value)
