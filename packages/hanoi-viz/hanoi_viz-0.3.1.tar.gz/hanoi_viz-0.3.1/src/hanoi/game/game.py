"""Main game logic for Towers of Hanoi."""

from __future__ import annotations

from collections import defaultdict

import pygame
from rich.console import Console

from hanoi import hanoi
from hanoi.cli import Settings

from .colors import Color
from .constants import (
    BOARD_HEIGHT,
    BOARD_POS_LEFT,
    BOARD_POS_TOP,
    BOARD_WIDTH,
    DISC_HEIGHT,
    DISC_WIDTH,
    FPS,
    HEIGHT,
    LIFT_Y,
    PEG_HEIGHT,
    PEG_WIDTH,
    WIDTH,
)
from .exceptions import QuitGame, ReturnToStartScreen

console = Console()


class Game:
    """Main game class for Towers of Hanoi."""

    def __init__(self, settings: Settings):
        self.settings = settings
        # pygame.init() is called in run_pygame, so we don't need to call it here
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.board = pygame.Rect(BOARD_POS_LEFT, BOARD_POS_TOP, BOARD_WIDTH, BOARD_HEIGHT)
        self.pegs = self._init_pegs()
        self.disks = self._init_discs(self.settings.n_disks)

        self.peg_stacks = defaultdict(list)
        self.peg_stacks[1].extend(self.disks)

        self.print_spaces = len(str(2**self.settings.n_disks - 1))
        self.print_disk_spaces = len(str(self.settings.n_disks))
        self.clock = pygame.time.Clock()

        self.finished = False
        self.paused = False
        self.step_once = False

        # Initialize font for text display
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.current_move_text = None

        self._update_caption()

    def _init_pegs(self) -> list[pygame.Rect]:
        """Initialize the three pegs."""
        return [
            pygame.Rect(peg_num * WIDTH // 4, PEG_HEIGHT, PEG_WIDTH, self.board.top - PEG_HEIGHT)
            for peg_num in range(1, 4)
        ]

    def _init_discs(self, n_discs: int) -> list[pygame.Rect]:
        """Initialize the discs."""
        discs = []
        for i in range(n_discs, 0, -1):
            width = DISC_WIDTH if i == n_discs else int(discs[-1].width * 0.9)
            disc = pygame.Rect(0, 0, width, DISC_HEIGHT)
            disc.centerx = self.pegs[0].centerx
            disc.bottom = self.board.top if i == n_discs else discs[-1].top
            discs.append(disc)
        return discs

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise QuitGame
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    raise QuitGame
                if event.key in (pygame.K_SPACE, pygame.K_p):
                    self.paused = not self.paused
                    if not self.paused:
                        # Resuming from pause - exit step mode to allow continuous running
                        self.step_once = False
                    self._update_caption()
                if event.key in (pygame.K_RIGHT, pygame.K_n):
                    self.step_once = True
                    if self.paused:
                        self.paused = False
                    self._update_caption()
                if event.key == pygame.K_r:
                    raise ReturnToStartScreen

    def _update_caption(self) -> None:
        """Update the window caption based on game state."""
        caption = 'Towers of Hanoi'
        if not self.finished:
            if self.step_once:
                caption += '(Step)'
            elif self.paused:
                caption += ' (Paused)'
        pygame.display.set_caption(caption)

    def wait_if_paused(self) -> None:
        """Wait while the game is paused."""
        while self.paused:
            self.handle_events()
            self.refresh()

    def run(self) -> None:
        """Run the main game loop."""
        while True:
            self.refresh()
            move_iterator = enumerate(hanoi(self.settings.n_disks), 1)
            i = 0

            while True:
                self.handle_events()

                # If paused, wait (unless step_once is triggered, which will unpause)
                if self.paused and not self.step_once:
                    self.refresh()
                    continue

                # Execute next move
                try:
                    i, (disc, from_, to) = next(move_iterator)
                    move_text = (
                        f'{i:{self.print_spaces}}: Move disc {disc:{self.print_disk_spaces}} from peg {from_} to {to}.'
                    )
                    console.print(move_text)
                    self.current_move_text = move_text
                    self.move_disc(from_, to)

                    # If in step mode, pause after completing the move
                    if self.step_once:
                        self._update_caption()
                        self.paused = True
                        self.step_once = False
                except StopIteration:
                    self.finished = True
                    suffix = 's' if self.settings.n_disks > 1 else ''
                    completion_text = f'{self.settings.n_disks} disc{suffix} solved in {i} move{suffix}.'
                    console.print(f'\n[green]{completion_text}')
                    self.current_move_text = completion_text
                    while True:  # Wait for restart or quit
                        self.handle_events()
                        self.refresh()

    def refresh(self) -> None:
        """Refresh the game display."""
        self.screen.fill(Color.WHITE)
        pygame.draw.rect(self.screen, Color.BLACK, self.board)
        for peg in self.pegs:
            pygame.draw.rect(self.screen, Color.BLACK, peg)
        for i, disc in enumerate(self.disks):
            pygame.draw.rect(self.screen, Color.DISC_COLORS[i % len(Color.DISC_COLORS)], disc)

        # Display current move text
        if self.current_move_text:
            text_surface = self.font.render(self.current_move_text, True, Color.BLACK)
            text_rect = text_surface.get_rect()
            text_rect.centerx = WIDTH // 2
            text_rect.centery = HEIGHT // 5
            self.screen.blit(text_surface, text_rect)

        pygame.display.flip()
        self.clock.tick(FPS)

    def _step_towards(
        self,
        rect: pygame.Rect,
        *,
        x: int | None = None,
        y: int | None = None,
        bottom: int | None = None,
    ) -> bool:
        """Move a rect one step towards the target position. Returns True if reached."""
        speed = self.settings.speed

        def approach(current: int, target: int) -> tuple[int, bool]:
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
    ) -> None:
        """Animate a rect to a target position."""
        done = False
        while not done:
            self.handle_events()
            self.wait_if_paused()
            done = self._step_towards(rect, x=x, y=y, bottom=bottom)
            self.refresh()

    def move_disc(self, from_peg: int, to_peg: int) -> None:
        """Move a disc from one peg to another."""
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
