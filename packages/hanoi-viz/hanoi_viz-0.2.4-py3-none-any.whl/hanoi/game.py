from __future__ import annotations

from collections import defaultdict
from typing import Final

import pygame
from rich import print

from hanoi import hanoi
from hanoi.cli import Settings

# -----------------------------
# Constants
# -----------------------------
FPS: Final[int] = 60

WIDTH: Final[int] = 600
HEIGHT: Final[int] = 400


BOARD_POS_LEFT: Final[int] = int(0.1 * WIDTH)
BOARD_POS_TOP: Final[int] = int(0.9 * HEIGHT)
BOARD_WIDTH: Final[int] = WIDTH - 2 * BOARD_POS_LEFT
BOARD_HEIGHT: Final[int] = int(0.02 * HEIGHT)


PEG_HEIGHT: Final[int] = HEIGHT // 2
PEG_WIDTH: Final[int] = 6

DISC_HEIGHT: Final[int] = 10
DISC_WIDTH: Final[int] = 120

LIFT_Y: Final[int] = HEIGHT // 3


class QuitGame(Exception):
    """Raised to stop the game loop cleanly when the window is closed."""


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (143, 143, 143)
    RED = (168, 50, 50)
    ORANGE = (207, 138, 21)
    BURNT_ORANGE = (255, 132, 0)
    YELLOW = (201, 193, 26)
    GREEN = (70, 189, 19)
    BLUE = (19, 150, 194)
    LIGHT_BLUE = (42, 191, 250)
    PURPLE = (153, 13, 191)
    LIGHT_PURPLE = (207, 99, 190)

    DISC_COLORS = [
        RED,
        ORANGE,
        YELLOW,
        GREEN,
        BLUE,
        PURPLE,
        GREY,
        BURNT_ORANGE,
        LIGHT_BLUE,
        LIGHT_PURPLE,
    ]


class Game:
    def __init__(self, settings: Settings):
        self.settings = settings
        pygame.init()
        pygame.display.set_caption('Towers of Hanoi')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.board = pygame.Rect(BOARD_POS_LEFT, BOARD_POS_TOP, BOARD_WIDTH, BOARD_HEIGHT)
        self.pegs = self.init_pegs()
        self.disks = self.init_discs(self.settings.n_disks)

        self.peg_stacks = defaultdict(list)
        self.peg_stacks[1].extend(self.disks)

        self.print_spaces = len(str(2**self.settings.n_disks - 1))
        self.print_disk_spaces = len(str(self.settings.n_disks))
        self.clock = pygame.time.Clock()

    def init_pegs(self) -> list[pygame.Rect]:
        return [
            pygame.Rect(peg_num * WIDTH // 4, PEG_HEIGHT, PEG_WIDTH, self.board.top - PEG_HEIGHT)
            for peg_num in range(1, 4)
        ]

    def init_discs(self, n_discs) -> list[pygame.Rect]:
        discs = []
        for i in range(n_discs, 0, -1):
            width = DISC_WIDTH if i == n_discs else int(discs[-1].width * 0.9)
            disc = pygame.Rect(0, 0, width, DISC_HEIGHT)
            disc.centerx = self.pegs[0].centerx
            disc.bottom = self.board.top if i == n_discs else discs[-1].top
            discs.append(disc)
        return discs

    @staticmethod
    def check_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise QuitGame

    def run(self):
        self.refresh()
        for i, (disc, from_, to) in enumerate(hanoi(self.settings.n_disks), 1):
            print(f'{i:{self.print_spaces}}: Move disc {disc:{self.print_disk_spaces}} from peg {from_} to {to}.')
            self.move_disc(from_, to)
        else:
            print(f'\n[green]{self.settings.n_disks} discs solved in {i} moves.')

        while True:
            self.check_events()
            self.refresh()

    def refresh(self):
        self.screen.fill(Color.WHITE)
        pygame.draw.rect(self.screen, Color.BLACK, self.board)
        for peg in self.pegs:
            pygame.draw.rect(self.screen, Color.BLACK, peg)
        for i, disc in enumerate(self.disks):
            pygame.draw.rect(self.screen, Color.DISC_COLORS[i % len(Color.DISC_COLORS)], disc)
        pygame.display.flip()
        self.clock.tick(FPS)

    def _step_towards(
        self,
        rect: pygame.Rect,
        *,
        x: int | None = None,
        y: int | None = None,
        bottom: int | None = None,
    ):
        speed = self.settings.speed

        def approach(current: int, target: int):
            if current == target or abs(target - current) <= speed:
                return target, True
            return (current + speed if target > current else current - speed), False

        done = True
        if x is not None:
            rect.centerx, ok = approach(rect.centerx, x)
            done &= ok
        if y is not None:
            rect.centery, ok = approach(rect.centery, y)
            done &= ok
        if bottom is not None:
            rect.bottom, ok = approach(rect.bottom, bottom)
            done &= ok
        return done

    def _animate_to(
        self,
        rect: pygame.Rect,
        *,
        x: int | None = None,
        y: int | None = None,
        bottom: int | None = None,
    ):
        while True:
            self.check_events()
            done = self._step_towards(rect, x=x, y=y, bottom=bottom)
            self.refresh()
            if done:
                return

    def move_disc(self, from_peg, to_peg):
        disc = self.peg_stacks[from_peg].pop()
        self._animate_to(disc, y=LIFT_Y)

        to_x = self.pegs[to_peg - 1].centerx
        self._animate_to(disc, x=to_x)

        try:
            top_disk = self.peg_stacks[to_peg][-1]
            to_y = top_disk.top
        except IndexError:
            to_y = self.board.top
        self._animate_to(disc, bottom=to_y)
        self.peg_stacks[to_peg].append(disc)


def run_pygame(settings: Settings):
    try:
        game = Game(settings)
        game.run()
    except QuitGame:
        print('[blue]quitting game...')
    except KeyboardInterrupt:
        print('[yellow]interrupted, quitting game...')
