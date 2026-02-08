import random

import pygame

from .config import SimConfig
from .game import create_game, step_game
from .render import draw_state


def run(config: SimConfig | None = None) -> None:
    config = config or SimConfig()
    rng = random.Random(config.random_seed)

    pygame.init()
    screen = pygame.display.set_mode((config.window_width, config.window_height))
    pygame.display.set_caption("RPS Battle")
    clock = pygame.time.Clock()

    state = create_game(config)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        state = step_game(state, rng)
        draw_state(screen, state, config)
        pygame.display.flip()
        clock.tick(config.fps)

    pygame.quit()
