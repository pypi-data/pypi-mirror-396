import pytest

from static_error_handler import Err, Ok, Result, panic


def test_ok_basic_predicates_and_extractors() -> None:
    r: Result[int, str] = Ok(123)

    assert r.is_ok() is True
    assert r.is_err() is False

    assert r.ok() == 123
    assert r.err() is None

    assert r.is_ok_and(lambda x: x > 100) is True
    assert r.is_ok_and(lambda x: x < 0) is False
    assert r.is_err_and(lambda e: True) is False


def test_err_basic_predicates_and_extractors() -> None:
    r: Result[int, str] = Err("boom")

    assert r.is_ok() is False
    assert r.is_err() is True

    assert r.ok() is None
    assert r.err() == "boom"

    assert r.is_ok_and(lambda x: True) is False
    assert r.is_err_and(lambda e: e == "boom") is True


def test_map_and_map_err() -> None:
    ok: Result[int, str] = Ok(10)
    err: Result[int, str] = Err("nope")

    assert ok.map(lambda x: x + 1).unwrap() == 11
    assert err.map(lambda x: x + 1).unwrap_err() == "nope"

    assert ok.map_err(lambda e: f"wrapped:{e}").unwrap() == 10
    assert err.map_err(lambda e: f"wrapped:{e}").unwrap_err() == "wrapped:nope"


def test_map_or_and_map_or_else() -> None:
    ok: Result[int, str] = Ok(7)
    err: Result[int, str] = Err("bad")

    assert ok.map_or(0, lambda x: x * 2) == 14
    assert err.map_or(0, lambda x: x * 2) == 0

    assert ok.map_or_else(lambda e: 0, lambda x: x * 3) == 21
    assert err.map_or_else(lambda e: len(e), lambda x: x * 3) == 3


def test_unwrap_and_expect_on_ok() -> None:
    r: Result[int, str] = Ok(1)

    assert r.unwrap() == 1
    assert r.expect("should not fail") == 1

    with pytest.raises(RuntimeError, match=r"Panic:"):
        r.unwrap_err()

    with pytest.raises(RuntimeError, match=r"Panic:"):
        r.expect_err("expected error")


def test_unwrap_and_expect_on_err() -> None:
    r: Result[int, str] = Err("e")

    assert r.unwrap_err() == "e"
    assert r.expect_err("should not fail") == "e"

    with pytest.raises(RuntimeError, match=r"Panic:"):
        r.unwrap()

    with pytest.raises(RuntimeError, match=r"Panic:"):
        r.expect("expected ok")


def test_and_and_then() -> None:
    ok: Result[int, str] = Ok(2)
    err: Result[int, str] = Err("x")

    assert ok.and_(Ok("next")).unwrap() == "next"
    assert err.and_(Ok("next")).unwrap_err() == "x"

    assert ok.and_then(lambda x: Ok(x * 10)).unwrap() == 20
    assert ok.and_then(lambda x: Err("no")).unwrap_err() == "no"
    assert err.and_then(lambda x: Ok(x * 10)).unwrap_err() == "x"


def test_or_or_else() -> None:
    ok: Result[int, str] = Ok(5)
    err: Result[int, str] = Err("fail")

    assert ok.or_(Ok(99)).unwrap() == 5
    assert err.or_(Ok(99)).unwrap() == 99

    assert ok.or_else(lambda e: Ok(77)).unwrap() == 5
    assert err.or_else(lambda e: Ok(len(e))).unwrap() == 4


def test_unwrap_or_and_unwrap_or_else() -> None:
    ok: Result[int, str] = Ok(3)
    err: Result[int, str] = Err("abcd")

    assert ok.unwrap_or(0) == 3
    assert err.unwrap_or(0) == 0

    assert ok.unwrap_or_else(lambda e: 0) == 3
    assert err.unwrap_or_else(lambda e: len(e)) == 4


def test_inspect_and_inspect_err_side_effects() -> None:
    seen: list[int] = []
    seen_err: list[str] = []

    ok: Result[int, str] = Ok(9)
    err: Result[int, str] = Err("oops")

    ok.inspect(lambda x: seen.append(x))
    err.inspect(lambda x: seen.append(x))  # should not run

    ok.inspect_err(lambda e: seen_err.append(e))  # should not run
    err.inspect_err(lambda e: seen_err.append(e))

    assert seen == [9]
    assert seen_err == ["oops"]


def test_panic_helper() -> None:
    with pytest.raises(RuntimeError, match=r"Panic: hello"):
        panic("hello")


def test_runtime_protocol_check() -> None:
    # This passes only if Result is decorated with @runtime_checkable.
    assert isinstance(Ok(1), Result)
    assert isinstance(Err("e"), Result)
