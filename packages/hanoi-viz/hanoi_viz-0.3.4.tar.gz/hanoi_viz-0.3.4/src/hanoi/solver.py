from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Tuple

Move = Tuple[int, int, int]


def hanoi(discs: int) -> Iterator[Move]:
    if discs < 1:
        return iter(())

    def _hanoi(disc: int, from_: int, to: int, via: int) -> Iterator[Move]:
        if disc == 1:
            yield disc, from_, to
        else:
            yield from _hanoi(disc - 1, from_, via, to)
            yield disc, from_, to
            yield from _hanoi(disc - 1, via, to, from_)

    return _hanoi(discs, 1, 3, 2)


if __name__ == '__main__':
    discs = 9
    start = time.perf_counter()

    for i, (disc, from_, to) in enumerate(hanoi(discs), 1):
        print(f'{i:,}: Move disc {disc} from peg {from_} to {to}.')

    end = time.perf_counter()

    print(f'\n{discs} discs took {end - start:.2f} seconds to solve.')
