import functools
import itertools
from typing import Iterator, Callable, TypeVar

U = TypeVar("U")
T = TypeVar("T")


class Iter(Iterator[T]):
    __slots__ = ("iterable",)

    def __init__(self, iterable: Iterator[T]):
        self.iterable = iterable

    def __iter__(self) -> Iterator[T]:
        return self.iterable

    def __next__(self) -> T:
        return next(self.iterable)

    def filter(self, func: Callable[[T], bool]) -> "Iter[T]":
        self.iterable = filter(func, self.iterable)
        return self

    def map(self, func: Callable[[T], U]) -> "Iter[U]":
        return Iter(map(func, self.iterable))

    def flat_map(self, func: Callable[[T], Iterator[U]]) -> "Iter[U]":
        return Iter(y for x in self.iterable for y in func(x))

    def collect(self, t: Callable[[Iterator[T]], U] = list) -> U:
        return t(self.iterable)

    def any(self, func: Callable[[T], bool]) -> bool:
        return any(map(func, self.iterable))

    def all(self, func: Callable[[T], bool]) -> bool:
        return all(map(func, self.iterable))

    def find(self, func: Callable[[T], bool]) -> T:
        return next(filter(func, self.iterable))

    def try_find(self, func: Callable[[T], bool]) -> T | None:
        return next(filter(func, self.iterable), None)

    def fold(self, func: Callable[[T, T], T]) -> T:
        return functools.reduce(func, self.iterable)

    def ilen(self) -> int:
        return sum(1 for _ in self.iterable)

    def enumerate(self, start: int = 0) -> "Iter[tuple[int, T]]":
        return Iter(enumerate(self.iterable, start=start))

    def skip(self, n: int) -> "Iter[T]":
        for _ in range(n):
            next(self.iterable, None)
        return self

    def take(self, n: int) -> "Iter[T]":
        self.iterable = itertools.islice(self.iterable, n)
        return self

    def take_while(self, func: Callable[[T], bool]) -> "Iter[T]":
        self.iterable = itertools.takewhile(func, self.iterable)
        return self

    def drop_while(self, func: Callable[[T], bool]) -> "Iter[T]":
        self.iterable = itertools.dropwhile(func, self.iterable)
        return self

    def chain(self, other: Iterator[T]) -> "Iter[T]":
        self.iterable = itertools.chain(self.iterable, other)
        return self
