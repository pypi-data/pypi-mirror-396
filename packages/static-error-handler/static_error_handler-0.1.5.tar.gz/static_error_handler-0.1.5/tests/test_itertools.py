# tests/test_itertools.py
from static_error_handler import Err, Ok

# If your file is literally `src/itertools.py`, this import is correct:
from static_error_handler.itertools import process_results  # noqa: E402


def test_process_results_all_ok() -> None:
    items = [Ok(1), Ok(2), Ok(3)]

    out = process_results(items, lambda xs: sum(xs))

    assert out.is_ok()
    assert out.unwrap() == 6


def test_process_results_stops_on_first_err_and_returns_err() -> None:
    items = [Ok(1), Err("boom"), Ok(999)]

    def consume(xs):
        seen = []
        for x in xs:
            # If iteration continues past the Err, this would trigger.
            assert x != 999
            seen.append(x)
        return tuple(seen)

    out = process_results(items, consume)

    assert out.is_err()
    assert out.unwrap_err() == "boom"


def test_process_results_empty_iterable() -> None:
    out = process_results([], lambda xs: list(xs))

    assert out.is_ok()
    assert out.unwrap() == []
