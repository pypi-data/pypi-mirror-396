"""Tests for toolz.itertoolz to verify stubs work correctly."""

from collections.abc import Iterable, Iterator
from typing import Literal, assert_type

import pytest
import toolz.itertoolz as it


class TestRemove:
    """Tests for remove function."""

    def test_basic(self) -> None:
        """remove should return items where predicate is False."""

        def iseven(x: int) -> bool:
            return x % 2 == 0

        result = it.remove(iseven, [1, 2, 3, 4])

        _ = assert_type(result, Iterable[int])
        assert list(result) == [1, 3]


class TestAccumulate:
    """Tests for accumulate function."""

    def test_add(self) -> None:
        """accumulate should repeatedly apply binary function."""
        result = it.accumulate(int.__add__, [1, 2, 3, 4, 5])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [1, 3, 6, 10, 15]

    def test_mul(self) -> None:
        """accumulate with multiplication."""
        result = it.accumulate(int.__mul__, [1, 2, 3, 4, 5])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [1, 2, 6, 24, 120]

    def test_with_initial(self) -> None:
        """accumulate with an initial value."""
        result = it.accumulate(int.__add__, [1, 2, 3], -1)

        _ = assert_type(result, Iterator[int])
        assert list(result) == [-1, 0, 2, 5]

    def test_empty_with_initial(self) -> None:
        """accumulate on empty sequence with initial."""
        result = it.accumulate(int.__add__, [], 1)

        _ = assert_type(result, Iterator[int])
        assert list(result) == [1]


class TestGroupby:
    """Tests for groupby function."""

    def test_len(self) -> None:
        """groupby should group collection by key function."""
        names = ["Alice", "Bob", "Charlie", "Dan", "Edith", "Frank"]
        result = it.groupby(len, names)

        _ = assert_type(result, dict[int, list[str]])
        assert result == {
            3: ["Bob", "Dan"],
            5: ["Alice", "Edith", "Frank"],
            7: ["Charlie"],
        }

    def test_predicate(self) -> None:
        """groupby with a predicate function."""

        def iseven(x: int) -> bool:
            return x % 2 == 0

        result = it.groupby(iseven, [1, 2, 3, 4, 5, 6, 7, 8])

        _ = assert_type(result, dict[bool, list[int]])
        assert result == {False: [1, 3, 5, 7], True: [2, 4, 6, 8]}


class TestMergeSorted:
    """Tests for merge_sorted function."""

    def test_basic(self) -> None:
        """merge_sorted should merge and sort sorted collections."""
        result = it.merge_sorted([1, 3, 5], [2, 4, 6])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [1, 2, 3, 4, 5, 6]

    def test_strings(self) -> None:
        """merge_sorted with strings."""
        result = it.merge_sorted("abc", "abc", "abc")

        _ = assert_type(result, Iterator[str])
        assert "".join(result) == "aaabbbccc"

    def test_with_key(self) -> None:
        """merge_sorted with a key function."""

        def key_func(x: int) -> int:
            return x // 3

        result = it.merge_sorted([2, 3], [1, 3], key=key_func)

        _ = assert_type(result, Iterator[int])
        assert list(result) == [2, 1, 3, 3]


class TestInterleave:
    """Tests for interleave function."""

    def test_basic(self) -> None:
        """interleave should interleave sequences."""
        result = it.interleave([[1, 2], [3, 4]])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [1, 3, 2, 4]

    def test_strings(self) -> None:
        """interleave with strings of different lengths."""
        result = it.interleave(("ABC", "XY"))

        _ = assert_type(result, Iterator[str])
        assert "".join(result) == "AXBYC"


class TestUnique:
    """Tests for unique function."""

    def test_basic(self) -> None:
        """unique should return only unique elements."""
        input: tuple[int, ...] = (1, 2, 3)
        result = it.unique(input)

        _ = assert_type(result, Iterator[Literal[1, 2, 3]])
        assert tuple(result) == (1, 2, 3)

    def test_with_duplicates(self) -> None:
        """unique should remove duplicates."""
        result = it.unique((1, 2, 1, 3))

        _ = assert_type(result, Iterator[Literal[1, 2, 3]])
        assert tuple(result) == (1, 2, 3)

    def test_with_key(self) -> None:
        """unique with a key function."""
        result = it.unique(["cat", "mouse", "dog", "hen"], key=len)

        _ = assert_type(result, Iterator[str])
        assert tuple(result) == ("cat", "mouse")


class TestIsiterable:
    """Tests for isiterable function."""

    def test_list(self) -> None:
        """isiterable should return True for lists."""
        assert it.isiterable([1, 2, 3]) is True

    def test_string(self) -> None:
        """isiterable should return True for strings."""
        assert it.isiterable("abc") is True

    def test_int(self) -> None:
        """isiterable should return False for integers."""
        assert it.isiterable(5) is False


class TestIsdistinct:
    """Tests for isdistinct function."""

    def test_distinct(self) -> None:
        """isdistinct should return True for distinct values."""
        assert it.isdistinct([1, 2, 3]) is True

    def test_not_distinct(self) -> None:
        """isdistinct should return False for duplicate values."""
        assert it.isdistinct([1, 2, 1]) is False

    def test_string_not_distinct(self) -> None:
        """isdistinct with string containing duplicates."""
        assert it.isdistinct("Hello") is False

    def test_string_distinct(self) -> None:
        """isdistinct with string of unique characters."""
        assert it.isdistinct("World") is True


class TestTake:
    """Tests for take function."""

    def test_basic(self) -> None:
        """take should return first n elements."""
        result = it.take(2, [10, 20, 30, 40, 50])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [10, 20]


class TestTail:
    """Tests for tail function."""

    def test_basic(self) -> None:
        """tail should return last n elements."""
        result = it.tail(2, [10, 20, 30, 40, 50])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [40, 50]


class TestDrop:
    """Tests for drop function."""

    def test_basic(self) -> None:
        """drop should return sequence after first n elements."""
        result = it.drop(2, [10, 20, 30, 40, 50])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [30, 40, 50]


class TestTakeNth:
    """Tests for take_nth function."""

    def test_basic(self) -> None:
        """take_nth should return every nth item."""
        result = it.take_nth(2, [10, 20, 30, 40, 50])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [10, 30, 50]


class TestFirst:
    """Tests for first function."""

    def test_basic(self) -> None:
        """first should return first element."""
        result = it.first("ABC")

        _ = assert_type(result, str)
        assert result == "A"


class TestSecond:
    """Tests for second function."""

    def test_basic(self) -> None:
        """second should return second element."""
        result = it.second("ABC")

        _ = assert_type(result, str)
        assert result == "B"


class TestNth:
    """Tests for nth function."""

    def test_basic(self) -> None:
        """nth should return nth element."""
        result = it.nth(1, "ABC")

        _ = assert_type(result, str)
        assert result == "B"


class TestLast:
    """Tests for last function."""

    def test_basic(self) -> None:
        """last should return last element."""
        result = it.last("ABC")

        _ = assert_type(result, str)
        assert result == "C"


class TestGet:
    """Tests for get function."""

    def test_single(self) -> None:
        """get should return element at index."""
        result = it.get(1, "ABC")

        _ = assert_type(result, str)
        assert result == "B"

    def test_multiple_with_list(self) -> None:
        """get with list of indices should return tuple."""
        result = it.get([1, 2], "ABC")

        _ = assert_type(result, tuple[str, ...])
        assert result == ("B", "C")

    def test_multiple_with_tuple(self) -> None:
        """get with tuple of indices raises TypeError - toolz only accepts list."""

        with pytest.raises(TypeError):
            _ = it.get((1, 2), "ABC")

    def test_multiple_with_iterator(self) -> None:
        """get with iterator raises TypeError - toolz only accepts list."""

        with pytest.raises(TypeError):
            _ = it.get(iter([1, 2]), "ABC")

    def test_multiple_with_set(self) -> None:
        """get with set raises TypeError - toolz only accepts list."""

        with pytest.raises(TypeError):
            _ = it.get({1, 2}, "ABC")

    def test_dict(self) -> None:
        """get should work with dictionaries."""
        phonebook = {"Alice": "555-1234", "Bob": "555-5678", "Charlie": "555-9999"}

        result = it.get("Alice", phonebook)

        _ = assert_type(result, str)
        assert result == "555-1234"

    def test_dict_multiple(self) -> None:
        """get with multiple keys from dictionary."""
        phonebook = {"Alice": "555-1234", "Bob": "555-5678", "Charlie": "555-9999"}

        result = it.get(["Alice", "Bob"], phonebook)

        _ = assert_type(result, tuple[str, ...])
        assert result == ("555-1234", "555-5678")

    def test_with_default(self) -> None:
        """get with default for missing values."""
        phonebook = {"Alice": "555-1234", "Bob": "555-5678", "Charlie": "555-9999"}

        result = it.get(["Alice", "Dennis"], phonebook, None)

        _ = assert_type(result, tuple[str | None, ...])
        assert result == ("555-1234", None)


class TestConcat:
    """Tests for concat function."""

    def test_basic(self) -> None:
        """concat should concatenate iterables."""
        result = it.concat([[], [1], [2, 3]])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [1, 2, 3]


class TestConcatv:
    """Tests for concatv function."""

    def test_basic(self) -> None:
        """concatv is variadic version of concat."""
        result = it.concatv([], ["a"], ["b", "c"])

        _ = assert_type(result, Iterator[str])
        assert list(result) == ["a", "b", "c"]


class TestMapcat:
    """Tests for mapcat function."""

    def test_basic(self) -> None:
        """mapcat should apply func to sequences and concatenate."""

        def upper_chars(s: Iterable[str]) -> list[str]:
            return [c.upper() for c in s]

        result = it.mapcat(upper_chars, [["a", "b"], ["c", "d", "e"]])

        _ = assert_type(result, Iterator[str])
        assert list(result) == ["A", "B", "C", "D", "E"]

    def test_can_expand(self):
        def possibly_expands(item: int | list[int]) -> list[int]:
            if isinstance(item, int):
                return [item, item]
            return item

        result = it.mapcat(possibly_expands, [1, [2, 3], 4])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [1, 1, 2, 3, 4, 4]


class TestCons:
    """Tests for cons function."""

    def test_basic(self) -> None:
        """cons should add element to beginning of sequence."""
        result = it.cons(1, [2, 3])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [1, 2, 3]


class TestInterpose:
    """Tests for interpose function."""

    def test_basic(self) -> None:
        """interpose should introduce element between pairs."""
        result = it.interpose("a", [1, 2, 3])

        _ = assert_type(result, Iterator[int | Literal["a"]])
        assert list(result) == [1, "a", 2, "a", 3]


class TestFrequencies:
    """Tests for frequencies function."""

    def test_basic(self) -> None:
        """frequencies should count occurrences."""
        result = it.frequencies(["cat", "cat", "ox", "pig", "pig", "cat"])

        _ = assert_type(result, dict[str, int])
        assert result == {"cat": 3, "ox": 1, "pig": 2}


class TestReduceby:
    """Tests for reduceby function."""

    def test_add(self) -> None:
        """reduceby should group and reduce."""

        def iseven(x: int) -> bool:
            return x % 2 == 0

        data = [1, 2, 3, 4, 5]
        result = it.reduceby(iseven, int.__add__, data)

        _ = assert_type(result, dict[bool, int])
        assert result == {False: 9, True: 6}

    def test_mul(self) -> None:
        """reduceby with multiplication."""

        def iseven(x: int) -> bool:
            return x % 2 == 0

        data = [1, 2, 3, 4, 5]
        result = it.reduceby(iseven, int.__mul__, data)

        _ = assert_type(result, dict[bool, int])
        assert result == {False: 15, True: 8}


class TestIterate:
    """Tests for iterate function."""

    def test_basic(self) -> None:
        """iterate should repeatedly apply function."""

        def inc(x: int) -> int:
            return x + 1

        counter = it.iterate(inc, 0)

        _ = assert_type(counter, Iterator[int])
        assert next(counter) == 0
        assert next(counter) == 1
        assert next(counter) == 2

    def test_double(self) -> None:
        """iterate with doubling function."""

        def double(x: int) -> int:
            return x * 2

        powers_of_two = it.iterate(double, 1)

        _ = assert_type(powers_of_two, Iterator[int])
        assert next(powers_of_two) == 1
        assert next(powers_of_two) == 2
        assert next(powers_of_two) == 4
        assert next(powers_of_two) == 8


class TestSlidingWindow:
    """Tests for sliding_window function."""

    def test_basic(self) -> None:
        """sliding_window should return overlapping subsequences."""
        result = it.sliding_window(2, [1, 2, 3, 4])

        _ = assert_type(result, Iterator[tuple[int, ...]])
        assert list(result) == [(1, 2), (2, 3), (3, 4)]

    def test_mean(self) -> None:
        """sliding_window for computing sliding means."""

        def mean(seq: tuple[int, ...]) -> float:
            return float(sum(seq)) / len(seq)

        result = list(map(mean, it.sliding_window(2, [1, 2, 3, 4])))

        _ = assert_type(result, list[float])
        assert result == [1.5, 2.5, 3.5]


class TestPartition:
    """Tests for partition function."""

    def test_basic(self) -> None:
        """partition should split into tuples of length n."""
        result = it.partition(2, [1, 2, 3, 4])

        _ = assert_type(result, Iterator[tuple[int, ...]])
        assert list(result) == [(1, 2), (3, 4)]

    def test_drop_incomplete(self) -> None:
        """partition drops incomplete final tuple by default."""
        result = it.partition(2, [1, 2, 3, 4, 5])

        _ = assert_type(result, Iterator[tuple[int, ...]])
        assert list(result) == [(1, 2), (3, 4)]

    def test_with_pad(self) -> None:
        """partition with pad fills incomplete tuple."""
        result = it.partition(2, [1, 2, 3, 4, 5], pad=None)

        _ = assert_type(result, Iterator[tuple[int | None, ...]])
        assert list(result) == [(1, 2), (3, 4), (5, None)]


class TestPartitionAll:
    """Tests for partition_all function."""

    def test_basic(self) -> None:
        """partition_all should include all elements."""
        result = it.partition_all(2, [1, 2, 3, 4])

        _ = assert_type(result, Iterator[tuple[int, ...]])
        assert list(result) == [(1, 2), (3, 4)]

    def test_incomplete(self) -> None:
        """partition_all includes shorter final tuple."""
        result = it.partition_all(2, [1, 2, 3, 4, 5])

        _ = assert_type(result, Iterator[tuple[int, ...]])
        assert list(result) == [(1, 2), (3, 4), (5,)]


class TestPluck:
    """Tests for pluck function."""

    def test_single(self) -> None:
        """pluck should extract single key from dicts."""
        data = [{"id": 1, "name": "Cheese"}, {"id": 2, "name": "Pies"}]
        result = it.pluck("name", data)

        _ = assert_type(result, Iterator[str | int])
        assert list(result) == ["Cheese", "Pies"]

    def test_multiple_with_list(self) -> None:
        """pluck with list of indices."""
        result = it.pluck([0, 1], [[1, 2, 3], [4, 5, 7]])

        _ = assert_type(result, Iterator[tuple[int, ...]])
        assert list(result) == [(1, 2), (4, 5)]

    def test_multiple_with_tuple(self) -> None:
        """pluck with tuple of indices raises TypeError - toolz only accepts list."""
        with pytest.raises(TypeError):
            _ = list(it.pluck((0, 1), [[1, 2, 3], [4, 5, 7]]))

    def test_multiple_with_iterator(self) -> None:
        """pluck with iterator raises TypeError - toolz only accepts list."""
        with pytest.raises(TypeError):
            _ = list(it.pluck(iter([0, 1]), [[1, 2, 3], [4, 5, 7]]))

    def test_multiple_with_set(self) -> None:
        """pluck with set raises TypeError - toolz only accepts list."""
        with pytest.raises(TypeError):
            _ = list(it.pluck({0, 1}, [[1, 2, 3], [4, 5, 7]]))


class TestJoin:
    """Tests for join function."""

    def test_basic(self) -> None:
        """join should join two sequences on common attributes."""
        friends = [
            ("Alice", "Edith"),
            ("Alice", "Zhao"),
            ("Edith", "Alice"),
            ("Zhao", "Alice"),
            ("Zhao", "Edith"),
        ]

        cities = [
            ("Alice", "NYC"),
            ("Alice", "Chicago"),
            ("Dan", "Sydney"),
            ("Edith", "Paris"),
            ("Edith", "Berlin"),
            ("Zhao", "Shanghai"),
        ]

        result = it.join(it.second, friends, it.first, cities)

        _ = assert_type(result, Iterator[tuple[tuple[str, str], tuple[str, str]]])
        unique_result = sorted(set(result))

        expected = [
            (("Alice", "Edith"), ("Edith", "Berlin")),
            (("Alice", "Edith"), ("Edith", "Paris")),
            (("Alice", "Zhao"), ("Zhao", "Shanghai")),
            (("Edith", "Alice"), ("Alice", "Chicago")),
            (("Edith", "Alice"), ("Alice", "NYC")),
            (("Zhao", "Alice"), ("Alice", "Chicago")),
            (("Zhao", "Alice"), ("Alice", "NYC")),
            (("Zhao", "Edith"), ("Edith", "Berlin")),
            (("Zhao", "Edith"), ("Edith", "Paris")),
        ]

        assert unique_result == expected

    # TODO #15
    # https://github.com/mgrinshpon/toolz-stubs/issues/15
    # def test_outer(self) -> None:
    #     """join with outer join using defaults."""

    #     def identity(x: int) -> int:
    #         return x

    #     result = it.join(
    #         identity,
    #         [1, 2, 3],
    #         identity,
    #         [2, 3, 4],
    #         left_default=None,
    #         right_default=None,
    #     )

    #     _ = assert_type(result, Iterator[tuple[int | None, int | None]])
    #     result_list = list(result)

    #     assert (2, 2) in result_list
    #     assert (3, 3) in result_list
    #     assert (None, 4) in result_list
    #     assert (1, None) in result_list


class TestDiff:
    """Tests for diff function."""

    def test_basic(self) -> None:
        """diff should return items that differ between sequences."""
        result = it.diff([1, 2, 3], [1, 2, 10, 100])

        _ = assert_type(result, Iterator[tuple[int, ...]])
        assert list(result) == [(3, 10)]

    def test_with_default(self) -> None:
        """diff with default for shorter sequences."""
        result = it.diff([1, 2, 3], [1, 2, 10, 100], default=None)

        _ = assert_type(result, Iterator[tuple[int | None, ...]])
        assert list(result) == [(3, 10), (None, 100)]

    def test_with_key(self) -> None:
        """diff with key function."""
        result = it.diff(["apples", "bananas"], ["Apples", "Oranges"], key=str.lower)

        _ = assert_type(result, Iterator[tuple[str, ...]])
        assert list(result) == [("bananas", "Oranges")]


class TestTopk:
    """Tests for topk function."""

    def test_basic(self) -> None:
        """topk should find k largest elements."""
        result = it.topk(2, [1, 100, 10, 1000])

        _ = assert_type(result, tuple[int, ...])
        assert result == (1000, 100)

    def test_with_key(self) -> None:
        """topk with key function."""

        def key_func(x: str) -> int:
            return len(x)

        result = it.topk(2, ["Alice", "Bob", "Charlie", "Dan"], key=key_func)

        _ = assert_type(result, tuple[str, ...])
        assert result == ("Charlie", "Alice")


class TestPeek:
    """Tests for peek function."""

    def test_basic(self) -> None:
        """peek should retrieve next element without consuming."""
        seq = [0, 1, 2, 3, 4]
        first, seq_iter = it.peek(seq)

        _ = assert_type(first, int)
        _ = assert_type(seq_iter, Iterator[int])
        assert first == 0
        assert list(seq_iter) == [0, 1, 2, 3, 4]


class TestPeekn:
    """Tests for peekn function."""

    def test_basic(self) -> None:
        """peekn should retrieve next n elements without consuming."""
        seq = [0, 1, 2, 3, 4]
        first_two, seq_iter = it.peekn(2, seq)

        _ = assert_type(first_two, tuple[int, ...])
        _ = assert_type(seq_iter, Iterator[int])
        assert first_two == (0, 1)
        assert list(seq_iter) == [0, 1, 2, 3, 4]


class TestRandomSample:
    """Tests for random_sample function."""

    def test_deterministic(self) -> None:
        """random_sample with seed should be deterministic."""
        seq = list(range(100))
        result = it.random_sample(0.1, seq, random_state=2016)

        _ = assert_type(result, Iterator[int])
        result_list = list(result)
        assert result_list == [7, 9, 19, 25, 30, 32, 34, 48, 59, 60, 81, 98]

        # Same seed should give same result
        result2 = list(it.random_sample(0.1, seq, random_state=2016))
        assert result2 == result_list
