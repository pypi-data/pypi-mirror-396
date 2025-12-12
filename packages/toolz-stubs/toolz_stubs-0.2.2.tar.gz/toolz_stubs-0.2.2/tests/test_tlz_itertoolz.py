"""Tests for tlz.itertoolz to verify stubs work correctly."""

import collections.abc
from typing import assert_type, cast

import tlz


def test_first_second_last() -> None:
    """first, second, last should return correct elements."""
    nums = [1, 2, 3, 4, 5]

    f = tlz.first(nums)
    s = tlz.second(nums)
    la = tlz.last(nums)

    _ = assert_type(f, int)
    _ = assert_type(s, int)
    _ = assert_type(la, int)

    assert f == 1
    assert s == 2
    assert la == 5


def test_nth() -> None:
    """nth should return the element at index n."""
    nums = [10, 20, 30, 40]

    result = tlz.nth(2, nums)

    _ = assert_type(result, int)
    assert result == 30


def test_take() -> None:
    """take should return the first n elements."""
    nums = [1, 2, 3, 4, 5]

    taken = tlz.take(3, nums)
    result = list(taken)

    _ = assert_type(result, list[int])
    assert result == [1, 2, 3]


def test_drop() -> None:
    """drop should skip the first n elements."""
    nums = [1, 2, 3, 4, 5]

    dropped = tlz.drop(2, nums)
    result = list(dropped)

    _ = assert_type(result, list[int])
    assert result == [3, 4, 5]


def test_take_nth() -> None:
    """take_nth should return every nth element."""
    nums = [0, 1, 2, 3, 4, 5, 6]

    result = list(tlz.take_nth(2, nums))

    _ = assert_type(result, list[int])
    assert result == [0, 2, 4, 6]


def test_partition() -> None:
    """partition should split sequence into tuples of n."""
    nums = [1, 2, 3, 4, 5, 6]

    parts = tlz.partition(2, nums)
    result = list(parts)

    _ = assert_type(result, list[tuple[int, ...]])
    assert result == [(1, 2), (3, 4), (5, 6)]


def test_partition_all() -> None:
    """partition_all should include partial final tuple."""
    nums = [1, 2, 3, 4, 5]

    parts = tlz.partition_all(2, nums)
    result = list(parts)

    _ = assert_type(result, list[tuple[int, ...]])
    assert result == [(1, 2), (3, 4), (5,)]


def test_sliding_window() -> None:
    """sliding_window should return overlapping subsequences."""
    nums = [1, 2, 3, 4]

    windows = tlz.sliding_window(2, nums)
    result = list(windows)

    _ = assert_type(result, list[tuple[int, ...]])
    assert result == [(1, 2), (2, 3), (3, 4)]


def test_groupby() -> None:
    """groupby should group items by key function."""
    names = ["Alice", "Bob", "Charlie", "Dan"]

    grouped = tlz.groupby(len, names)

    _ = assert_type(grouped, dict[int, list[str]])
    assert grouped[3] == ["Bob", "Dan"]
    assert grouped[5] == ["Alice"]
    assert grouped[7] == ["Charlie"]


def test_frequencies() -> None:
    """frequencies should count occurrences."""
    items = ["cat", "dog", "cat", "bird", "cat"]

    freqs = tlz.frequencies(items)

    _ = assert_type(freqs, dict[str, int])
    assert freqs["cat"] == 3
    assert freqs["dog"] == 1
    assert freqs["bird"] == 1


def test_unique() -> None:
    """unique should return distinct elements in order."""
    nums = [1, 2, 1, 3, 2, 4, 1]

    result = list(tlz.unique(nums))

    _ = assert_type(result, list[int])
    assert result == [1, 2, 3, 4]


def test_concat() -> None:
    """concat should concatenate iterables."""
    lists: list[list[int]] = [[1, 2], [3, 4], [5]]

    result = list(tlz.concat(lists))

    _ = assert_type(result, list[int])
    assert result == [1, 2, 3, 4, 5]


def test_concatv() -> None:
    """concatv should concatenate variadic iterables."""
    result = list(tlz.concatv([1, 2], [3, 4], [5]))

    _ = assert_type(result, list[int])
    assert result == [1, 2, 3, 4, 5]


def test_interleave() -> None:
    """interleave should alternate between sequences."""
    result = list(tlz.interleave([[1, 2, 3], [10, 20, 30]]))

    _ = assert_type(result, list[int])
    assert result == [1, 10, 2, 20, 3, 30]


def test_interpose() -> None:
    """interpose should insert element between items."""
    result = list(tlz.interpose(cast(str, "x"), [1, 2, 3]))

    _ = assert_type(result, list[int | str])
    assert result == [1, "x", 2, "x", 3]


def test_get_single() -> None:
    """get with single index should return element."""
    seq = [10, 20, 30]

    result = tlz.get(1, seq)

    _ = assert_type(result, int)
    assert result == 20


def test_get_multiple() -> None:
    """get with multiple indices should return tuple."""
    seq = [10, 20, 30, 40]

    result = tlz.get([0, 2], seq)

    _ = assert_type(result, tuple[int, ...])
    assert result == (10, 30)


def test_topk() -> None:
    """topk should return the k largest elements."""
    nums = [3, 1, 4, 1, 5, 9, 2, 6]

    result = tlz.topk(3, nums)

    _ = assert_type(result, tuple[int, ...])
    assert result == (9, 6, 5)


def test_accumulate() -> None:
    # No default
    nums = [1, 2, 3, 4, 5]
    add = int.__add__

    result = list(tlz.accumulate(add, nums))

    _ = assert_type(result, list[int])
    assert result == [1, 3, 6, 10, 15]

    # With default
    dicts = [
        {
            "a": 1,
            "b": 2,
            "c": 3,
        },
        {
            "d": 4,
        },
        {
            "e": 5,
        },
    ]
    result2 = tlz.accumulate(tlz.merge, dicts, dict())
    _ = assert_type(result2, collections.abc.Iterator[dict[str, int]])
    assert list(result2)[3] == {
        "a": 1,
        "b": 2,
        "c": 3,
        "d": 4,
        "e": 5,
    }


def test_iterate() -> None:
    """iterate should repeatedly apply function."""

    def inc(x: int) -> int:
        return x + 1

    counter = tlz.iterate(inc, 0)

    result = [next(counter) for _ in range(5)]

    _ = assert_type(result, list[int])
    assert result == [0, 1, 2, 3, 4]


def test_count() -> None:
    """count should return the number of items."""
    nums = [1, 2, 3, 4, 5]

    result = tlz.count(nums)

    _ = assert_type(result, int)
    assert result == 5


def test_cons() -> None:
    """cons should prepend element to sequence."""
    result = list(tlz.cons(0, [1, 2, 3]))

    _ = assert_type(result, list[int])
    assert result == [0, 1, 2, 3]


def test_remove() -> None:
    """remove should filter out items matching predicate."""

    def is_even(x: int) -> bool:
        return x % 2 == 0

    result = list(tlz.remove(is_even, [1, 2, 3, 4, 5]))

    _ = assert_type(result, list[int])
    assert result == [1, 3, 5]


def test_peek() -> None:
    """peek should return first element and full iterator."""
    seq = [1, 2, 3]

    first, iterator = tlz.peek(seq)
    result = list(iterator)

    _ = assert_type(first, int)
    _ = assert_type(result, list[int])
    assert first == 1
    assert result == [1, 2, 3]


def test_peekn() -> None:
    """peekn should return first n elements and full iterator."""
    seq = [1, 2, 3, 4, 5]

    first_two, iterator = tlz.peekn(2, seq)
    result = list(iterator)

    _ = assert_type(first_two, tuple[int, ...])
    _ = assert_type(result, list[int])
    assert first_two == (1, 2)
    assert result == [1, 2, 3, 4, 5]


def test_diff() -> None:
    """diff should return elements that differ between sequences."""
    seq1 = [1, 2, 3]
    seq2 = [1, 2, 10]

    result = list(tlz.diff(seq1, seq2))

    _ = assert_type(result, list[tuple[int, ...]])
    assert result == [(3, 10)]


def test_reduceby() -> None:
    """reduceby should group and reduce by key function."""

    def is_even(x: int) -> bool:
        return x % 2 == 0

    add = int.__add__
    nums = [1, 2, 3, 4, 5]

    result = tlz.reduceby(is_even, add, nums)

    _ = assert_type(result, dict[bool, int])
    assert result[True] == 6  # 2 + 4
    assert result[False] == 9  # 1 + 3 + 5


def test_join() -> None:
    """join should join two sequences on common keys."""
    left = [(1, 10), (2, 20), (3, 30)]
    right = [(1, 100), (2, 200), (4, 400)]

    def left_key(x: tuple[int, int]) -> int:
        return x[0]

    def right_key(x: tuple[int, int]) -> int:
        return x[0]

    result = list(tlz.join(left_key, left, right_key, right))

    _ = assert_type(result, list[tuple[tuple[int, int], tuple[int, int]]])
    assert (1, 10) in [r[0] for r in result]
    assert (1, 100) in [r[1] for r in result]
