from typing import final

import pytest

from epublib.exceptions import EPUBError
from epublib.resources.window import Window

type BW = tuple[list[int], Window[int, int]]


@final
class TestWindow:
    @pytest.fixture
    def base_and_window(self) -> BW:
        base = [1, 2, 3, 4, 5, 6, 7, 8]
        win = Window[int, int](
            base, lambda x: x % 2 == 0, lambda x: "Only even numbers allowed"
        )
        return base, win

    def test_len_and_iter(self, base_and_window: BW) -> None:
        _, win = base_and_window
        assert len(win) == 4
        assert list(win) == [2, 4, 6, 8]

    def test_empty_window(self) -> None:
        base = [1, 3, 5, 7, 9, 11]
        win = Window[int, int](
            base, lambda x: x % 2 == 0, lambda x: "Only even numbers allowed"
        )
        assert len(win) == 0
        win.insert(0, 2)
        assert len(win) == 1
        assert 2 in base

    def test_getitem_int_and_slice(self, base_and_window: BW) -> None:
        _, win = base_and_window
        assert win[0] == 2
        assert win[1] == 4
        assert win[-1] == 8
        assert win[1:3] == [4, 6]
        assert win[:] == [2, 4, 6, 8]

    def test_setitem(self, base_and_window: BW) -> None:
        base, win = base_and_window
        win[0] = 10
        assert base[1] == 10
        assert win[0] == 10

        with pytest.raises(EPUBError):
            win[0] = 11  # odd number not allowed

        win[1:3] = [12, 14]
        assert base[3] == 12
        assert base[5] == 14
        assert win[1] == 12
        assert win[2] == 14

        with pytest.raises(ValueError):
            win[1:3] = 16  # type: ignore[reportArgumentType]

        with pytest.raises(EPUBError):
            win[3] = 13

        with pytest.raises(EPUBError):
            win[1:3] = [12, 13]

    def test_delitem_int(self, base_and_window: BW) -> None:
        base, win = base_and_window
        del win[1]  # deletes 4
        assert base == [1, 2, 3, 5, 6, 7, 8]
        assert list(win) == [2, 6, 8]

    def test_delitem_slice(self, base_and_window: BW) -> None:
        base, win = base_and_window
        del win[1:3]  # deletes 4 and 6
        assert base == [1, 2, 3, 5, 7, 8]
        assert list(win) == [2, 8]

    def test_insert(self, base_and_window: BW) -> None:
        base, win = base_and_window

        win.insert(1, 10)
        assert 10 in base
        assert base.index(2) < base.index(10) < base.index(4)
        assert list(win) == [2, 10, 4, 6, 8]

        win.insert(len(win), 12)  # append at end
        assert 12 in base
        assert all(base.index(x) < base.index(12) for x in [2, 4, 6, 8, 10])

        win.insert(0, 14)
        assert 14 in base
        assert all(base.index(x) > base.index(14) for x in win if x != 14)
        assert list(win) == [14, 2, 10, 4, 6, 8, 12]
        assert win[0] == 14

        with pytest.raises(EPUBError):
            win.insert(0, 11)  # odd number not allowed

    def test_append(self, base_and_window: BW) -> None:
        base, win = base_and_window
        win.append(12)
        assert 12 in base
        assert all(base.index(x) < base.index(12) for x in [2, 4, 6, 8])

    def test_reversed(self, base_and_window: BW) -> None:
        _, win = base_and_window

        assert list(reversed(win)) == [8, 6, 4, 2]
