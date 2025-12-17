from collections.abc import Callable
from dataclasses import dataclass
from typing import NoReturn, Protocol, runtime_checkable


def panic(message: str) -> NoReturn:
    raise RuntimeError(f"Panic: {message}")


@runtime_checkable
class Result[T, E](Protocol):
    # Predicates
    def is_ok(self) -> bool: ...
    def is_ok_and(self, op: Callable[[T], bool]) -> bool: ...
    def is_err(self) -> bool: ...
    def is_err_and(self, op: Callable[[E], bool]) -> bool: ...

    # Extractors
    def ok(self) -> T | None: ...
    def err(self) -> E | None: ...

    # Transforms
    def map[U](self, op: Callable[[T], U]) -> "Result[U, E]": ...
    def map_or[U](self, default: U, op: Callable[[T], U]) -> U: ...
    def map_or_else[U](self, default: Callable[[E], U], op: Callable[[T], U]) -> U: ...
    def map_err[F](self, op: Callable[[E], F]) -> "Result[T, F]": ...

    # Unwrap / expect
    def expect(self, msg: str) -> T: ...
    def unwrap(self) -> T: ...
    def expect_err(self, msg: str) -> E: ...
    def unwrap_err(self) -> E: ...

    # Combinators
    def and_[U](self, res: "Result[U, E]") -> "Result[U, E]": ...
    def and_then[U](self, op: Callable[[T], "Result[U, E]"]) -> "Result[U, E]": ...
    def or_[F](self, res: "Result[T, F]") -> "Result[T, F]": ...
    def or_else[F](self, op: Callable[[E], "Result[T, F]"]) -> "Result[T, F]": ...

    # Defaults
    def unwrap_or(self, default: T) -> T: ...
    def unwrap_or_else(self, op: Callable[[E], T]) -> T: ...

    # Side effects
    def inspect(self, op: Callable[[T], None]) -> "Result[T, E]": ...
    def inspect_err(self, op: Callable[[E], None]) -> "Result[T, E]": ...


@dataclass
class Ok[T, E](Result[T, E]):
    value: T

    def is_ok(self) -> bool:
        return True

    def is_ok_and(self, op: Callable[[T], bool]) -> bool:
        return op(self.value)

    def is_err(self) -> bool:
        return False

    def is_err_and(self, op: Callable[[E], bool]) -> bool:
        return False

    def ok(self) -> T | None:
        return self.value

    def err(self) -> E | None:
        return None

    def map[U](self, op: Callable[[T], U]) -> Result[U, E]:
        return Ok(op(self.value))

    def map_or[U](self, default: U, op: Callable[[T], U]) -> U:
        return op(self.value)

    def map_or_else[U](self, default: Callable[[E], U], op: Callable[[T], U]) -> U:
        return op(self.value)

    def map_err[F](self, op: Callable[[E], F]) -> Result[T, F]:
        return Ok(self.value)

    def expect(self, msg: str) -> T:
        return self.value

    def unwrap(self) -> T:
        return self.value

    def expect_err(self, msg: str) -> E:
        panic(msg)

    def unwrap_err(self) -> E:
        panic("unwrap_err")

    def and_[U](self, res: Result[U, E]) -> Result[U, E]:
        return res

    def and_then[U](self, op: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return op(self.value)

    def or_[F](self, res: Result[T, F]) -> Result[T, F]:
        return Ok(self.value)

    def or_else[F](self, op: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return Ok(self.value)

    def unwrap_or(self, default: T) -> T:
        return self.value

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return self.value

    def inspect(self, op: Callable[[T], None]) -> Result[T, E]:
        op(self.value)
        return self

    def inspect_err(self, op: Callable[[E], None]) -> Result[T, E]:
        return self


@dataclass
class Err[T, E](Result[T, E]):
    error: E

    def is_ok(self) -> bool:
        return False

    def is_ok_and(self, op: Callable[[T], bool]) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def is_err_and(self, op: Callable[[E], bool]) -> bool:
        return op(self.error)

    def ok(self) -> T | None:
        return None

    def err(self) -> E | None:
        return self.error

    def map[U](self, op: Callable[[T], U]) -> Result[U, E]:
        return Err(self.error)

    def map_or[U](self, default: U, op: Callable[[T], U]) -> U:
        return default

    def map_or_else[U](self, default: Callable[[E], U], op: Callable[[T], U]) -> U:
        return default(self.error)

    def map_err[F](self, op: Callable[[E], F]) -> Result[T, F]:
        return Err(op(self.error))

    def expect(self, msg: str) -> T:
        panic(msg)

    def unwrap(self) -> T:
        panic("unwrap")

    def expect_err(self, msg: str) -> E:
        return self.error

    def unwrap_err(self) -> E:
        return self.error

    def and_[U](self, res: Result[U, E]) -> Result[U, E]:
        return Err(self.error)

    def and_then[U](self, op: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return Err(self.error)

    def or_[F](self, res: Result[T, F]) -> Result[T, F]:
        return res

    def or_else[F](self, op: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return op(self.error)

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        return op(self.error)

    def inspect(self, op: Callable[[T], None]) -> Result[T, E]:
        return self

    def inspect_err(self, op: Callable[[E], None]) -> Result[T, E]:
        op(self.error)
        return self


__all__ = ["Err", "Ok", "Result", "panic"]
