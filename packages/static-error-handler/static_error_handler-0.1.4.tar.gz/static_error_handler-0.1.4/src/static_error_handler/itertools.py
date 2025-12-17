from typing import Callable, Iterable, TypeVar, Any
from static_error_handler import Result, Ok, Err

# Generic Types
T = TypeVar("T")
E = TypeVar("E")
R = TypeVar("R")

def process_results(
    iterable: Iterable[Result[T, E]], 
    func: Callable[[Iterable[T]], R]
) -> Result[R, E]:
    """
    Adapts an iterable of Results into an iterable of values. 
    If an Err is encountered, iteration stops, and that Err is returned.
    """
    
    # 1. This list acts as our mutable memory slot (like &mut Option<E> in Rust)
    captured_error = []

    # 2. Define the "Shim" Generator
    def result_unwrapper():
        for item in iterable:
            if captured_error: 
                # Safety check: if we already found an error, stop yielding
                return

            if item.is_ok():
                yield item.unwrap()
            else:
                # Capture the error and STOP the generator (equivalent to returning None in Rust)
                captured_error.append(item.unwrap_err())
                return

    # 3. Pass the shim to the user's function
    # The user's function thinks it is getting a normal iterable of T
    computed_value = func(result_unwrapper())

    # 4. Check if the loop was broken by an error
    if captured_error:
        return Err(captured_error[0])
    
    # 5. If no error, wrap the result in Ok
    return Ok(computed_value)
