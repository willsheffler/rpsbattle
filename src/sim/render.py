import pygame

from .config import SimConfig
from .game import GameState, creature_counts
from .rps import CreatureType

_BG_COLOR = (240, 243, 247)
_GRID_COLOR = (200, 206, 214)
_COLOR_BY_TYPE = {
    CreatureType.ROCK: (220, 80, 80),
    CreatureType.PAPER: (70, 130, 210),
    CreatureType.SCISSORS: (70, 170, 90),
}
_TEXT_COLOR = (25, 30, 40)


def _draw_grid(screen: pygame.Surface, config: SimConfig) -> None:
    for x in range(config.board_width + 1):
        px = x * config.cell_size
        pygame.draw.line(screen, _GRID_COLOR, (px, 0), (px, config.window_height), 1)

    for y in range(config.board_height + 1):
        py = y * config.cell_size
        pygame.draw.line(screen, _GRID_COLOR, (0, py), (config.window_width, py), 1)


def _draw_creatures(screen: pygame.Surface, state: GameState, config: SimConfig) -> None:
    padding = max(2, config.cell_size // 8)
    size = config.cell_size - (padding * 2)

    for creature in state.creatures:
        x = creature.pos.x * config.cell_size + padding
        y = creature.pos.y * config.cell_size + padding
        rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(screen, _COLOR_BY_TYPE[creature.kind], rect)


def _draw_hud(screen: pygame.Surface, state: GameState) -> None:
    font = pygame.font.Font(None, 26)
    counts = creature_counts(state)
    label = (
        f"Tick: {state.tick}  "
        f"Rock: {counts[CreatureType.ROCK]}  "
        f"Paper: {counts[CreatureType.PAPER]}  "
        f"Scissors: {counts[CreatureType.SCISSORS]}"
    )
    text_surface = font.render(label, True, _TEXT_COLOR)
    screen.blit(text_surface, (8, 8))


def draw_state(screen: pygame.Surface, state: GameState, config: SimConfig) -> None:
    screen.fill(_BG_COLOR)
    _draw_grid(screen, config)
    _draw_creatures(screen, state, config)
    _draw_hud(screen, state)
