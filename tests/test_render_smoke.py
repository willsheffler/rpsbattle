import os

import pygame

from sim.config import SimConfig
from sim.game import create_game
from sim.render import draw_state


def test_draw_state_smoke() -> None:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    try:
        config = SimConfig(board_width=6, board_height=4, cell_size=16, creature_count=5)
        screen = pygame.display.set_mode((config.window_width, config.window_height))
        state = create_game(config)

        draw_state(screen, state, config)
        pygame.display.flip()

        assert screen.get_size() == (config.window_width, config.window_height)
    finally:
        pygame.quit()


def test_draw_state_with_debug_boundaries_smoke() -> None:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    try:
        config = SimConfig(
            board_width=6,
            board_height=4,
            cell_size=16,
            creature_count=5,
            obstacle_count=2,
            obstacle_avg_size=10,
        )
        screen = pygame.display.set_mode((config.window_width, config.window_height))
        state = create_game(config)

        draw_state(screen, state, config, show_debug_boundaries=True)
        pygame.display.flip()

        assert screen.get_size() == (config.window_width, config.window_height)
    finally:
        pygame.quit()
