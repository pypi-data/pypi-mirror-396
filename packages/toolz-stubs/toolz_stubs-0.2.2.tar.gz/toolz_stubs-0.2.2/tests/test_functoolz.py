from typing import assert_type

import tlz
import toolz


def test_basic_identity():
    """Type checker should correctly infer types for identity."""
    x = toolz.identity(5)
    _ = assert_type(x, int)

    y = tlz.identity("hello")
    _ = assert_type(y, str)


def test_compose_left():
    composed_func = toolz.compose_left(str.strip, str.upper)
    result = composed_func("  hello world  ")
    assert result == "HELLO WORLD"


def test_compose():
    """Test compose with type assertions."""
    composed = toolz.compose(str.upper, str.strip)
    _ = assert_type(composed("  hello  "), str)


class TestPipe:
    def test_pipe_two_functions_type_inference(self):
        """pipe(data, f0, f1) should infer T0->T1->T2 correctly."""

        def int_to_str(x: int) -> str:
            return str(x)

        def str_to_float(s: str) -> float:
            return float(s)

        result = toolz.pipe(42, int_to_str, str_to_float)
        _ = assert_type(result, float)
        assert result == 42.0

    def test_pipe_three_functions_type_inference(self):
        """pipe(data, f1, f2, f3) should infer T0 -> T1 -> T2 -> T3 correctly."""

        def int_to_str(x: int) -> str:
            return str(x)

        def str_to_float(s: str) -> float:
            return float(s)

        def float_to_bool(f: float) -> bool:
            return f > 0

        result = toolz.pipe(42, int_to_str, str_to_float, float_to_bool)
        _ = assert_type(result, bool)
        assert result

    def test_pipe_with_list_transformation(self):
        """pipe() should correctly infer types through list transformations."""

        def double_all(xs: list[int]) -> list[int]:
            return [x * 2 for x in xs]

        def sum_all(xs: list[int]) -> int:
            return sum(xs)

        def to_string(x: int) -> str:
            return str(x)

        result = toolz.pipe([1, 2, 3], double_all, sum_all, to_string)
        _ = assert_type(result, str)
        assert result == "12"


class TestJuxt:
    """Tests for juxt function."""

    def test_basic(self) -> None:
        """juxt should apply multiple functions and return a tuple."""

        def inc(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        j = toolz.juxt(inc, double)
        result = j(10)

        _ = assert_type(result, tuple[int, int])
        assert result == (11, 20)

    def test_single_function(self) -> None:
        """juxt with single function should return single-element tuple."""

        def inc(x: int) -> int:
            return x + 1

        j = toolz.juxt(inc)
        result = j(10)

        _ = assert_type(result, tuple[int])
        assert result == (11,)

    def test_heterogeneous(self) -> None:
        """juxt should support functions with different return types."""

        def to_str(x: int) -> str:
            return str(x)

        def to_float(x: int) -> float:
            return float(x)

        def identity(x: int) -> int:
            return x

        j = toolz.juxt(to_str, to_float, identity)
        result = j(42)

        _ = assert_type(result, tuple[str, float, int])
        assert result == ("42", 42.0, 42)

    def test_list_input(self) -> None:
        """juxt should accept a list of functions (less precise typing)."""

        def inc(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        funcs = [inc, double]
        j = toolz.juxt(funcs)
        result = j(10)

        # List input can't have precise tuple length at type-check time
        _ = assert_type(result, tuple[int, ...])
        assert result == (11, 20)

    def test_empty(self) -> None:
        """juxt with no functions should return empty tuple."""
        j = toolz.juxt()
        result = j(10)

        _ = assert_type(result, tuple[()])
        assert result == ()
