from collections.abc import Callable, Generator, Iterable, Iterator, MutableSequence
from typing import Never, cast, overload, override

from epublib.exceptions import EPUBError


class Window[B, T](MutableSequence[T]):
    def __init__(
        self,
        base: MutableSequence[B],
        predicate: Callable[[B], bool],
        doesnt_satisfy_error_msg: Callable[[B], str],
    ):
        self._base: MutableSequence[T] = cast(MutableSequence[T], base)
        self._predicate: Callable[[T], bool] = cast(Callable[[T], bool], predicate)
        self.doesnt_satisfy_error_msg: Callable[[T], str] = cast(
            Callable[[T], str],
            doesnt_satisfy_error_msg,
        )

    def raise_predicate_error(self, value: T) -> Never:
        raise EPUBError(self.doesnt_satisfy_error_msg(value))

    def _indices(self) -> Generator[int]:
        """Indices of base elements that satisfy the predicate."""
        return (i for i, v in enumerate(self._base) if self._predicate(v))

    @overload
    def __getitem__(self, index: int) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> MutableSequence[T]: ...

    @override
    def __getitem__(self, index: int | slice) -> T | MutableSequence[T]:
        indices = list(self._indices())
        if isinstance(index, slice):
            return [self._base[i] for i in indices[index]]
        return self._base[indices[index]]

    @overload
    def __setitem__(self, index: int, value: T) -> None: ...
    @overload
    def __setitem__(self, index: slice, value: Iterable[T]) -> None: ...

    @override
    def __setitem__(self, index: int | slice, value: T | Iterable[T]) -> None:
        indices = list(self._indices())

        if isinstance(index, slice) and isinstance(value, Iterable):
            iterable = iter(cast(Iterable[T], value))
            items: list[T] = []  # Collect to check all before inserting

            for v in iterable:
                if not self._predicate(v):
                    self.raise_predicate_error(v)
                items.append(v)

            for i, v in zip(indices[index], items):
                self._base[i] = v

        elif isinstance(index, int):
            value = cast(T, value)
            if not self._predicate(value):
                self.raise_predicate_error(value)

            self._base[indices[index]] = value

        else:
            raise ValueError(
                "Setting multiple items to a single index is not supported"
            )

    @override
    def __delitem__(self, index: int | slice) -> None:
        indices = list(self._indices())
        if isinstance(index, slice):
            indices = sorted(indices[index], reverse=True)
            for i in indices:
                del self._base[i]
        else:
            del self._base[indices[index]]

    @override
    def __len__(self) -> int:
        return len(list(self._indices()))

    @override
    def insert(self, index: int, value: T) -> None:
        if not self._predicate(value):
            self.raise_predicate_error(value)

        indices = list(self._indices())
        if not indices:
            # no matching elements yet → just append to base
            self._base.append(value)
        elif index >= len(indices):
            # append after last matching element
            last_match = indices[-1]
            self._base.insert(last_match + 1, value)
        else:
            # insert before the `index`th matching element
            self._base.insert(indices[index], value)

    @override
    def __iter__(self) -> Iterator[T]:
        indices = self._indices()
        for i in indices:
            yield self._base[i]

    @override
    def __reversed__(self) -> Iterator[T]:
        indices = reversed(tuple(self._indices()))
        for i in indices:
            yield self._base[i]
