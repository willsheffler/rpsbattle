from datetime import datetime
from pathlib import Path
import random

from .config import SimConfig
from .game import create_game, creature_counts, step_game
from .rps import CreatureType


def winner_kind_or_none(state) -> CreatureType | None:
    counts = creature_counts(state)
    alive = [kind for kind in CreatureType if counts[kind] > 0]
    if len(alive) == 1:
        return alive[0]
    return None


def _save_screenshot(screen) -> Path:
    import pygame

    screenshot_dir = Path("screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    file_path = screenshot_dir / f"rpsbattle-{timestamp}.png"
    pygame.image.save(screen, str(file_path))
    return file_path


def run(config: SimConfig | None = None) -> None:
    import pygame

    from .render import draw_state

    config = config or SimConfig()
    rng = random.Random(config.random_seed)

    pygame.init()
    screen = pygame.display.set_mode((config.window_width, config.window_height))
    pygame.display.set_caption("RPS Battle")
    clock = pygame.time.Clock()

    state = create_game(config)
    running = True
    speed_multiplier = 1.0
    screenshot_requested = False

    while running:
        dt_seconds = clock.tick(config.fps) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:
                    speed_multiplier = max(0.25, speed_multiplier - 0.25)
                    print(f"Speed x{speed_multiplier:.2f}")
                elif event.key == pygame.K_RIGHTBRACKET:
                    speed_multiplier = min(4.0, speed_multiplier + 0.25)
                    print(f"Speed x{speed_multiplier:.2f}")
                elif event.key == pygame.K_p:
                    screenshot_requested = True

        state = step_game(
            state,
            rng,
            convert_loser_to_winner=config.convert_loser_to_winner,
            encounter_distance=config.creature_radius * 2,
            dt_seconds=dt_seconds * speed_multiplier * config.tps_multiplier,
        )
        draw_state(screen, state, config)
        pygame.display.flip()
        if screenshot_requested:
            file_path = _save_screenshot(screen)
            print(f"Screenshot saved: {file_path}")
            screenshot_requested = False

    pygame.quit()


def run_headless(
    config: SimConfig | None = None,
    max_ticks: int = 10_000,
    dt_seconds: float = 1.0 / 60.0,
) -> CreatureType | None:
    config = config or SimConfig()
    rng = random.Random(config.random_seed)
    state = create_game(config)

    for _ in range(max_ticks):
        winner = winner_kind_or_none(state)
        if winner is not None:
            print(f"Winner: {winner.value} at tick {state.tick}")
            return winner

        state = step_game(
            state,
            rng,
            convert_loser_to_winner=config.convert_loser_to_winner,
            encounter_distance=config.creature_radius * 2,
            dt_seconds=dt_seconds * config.tps_multiplier,
        )

    winner = winner_kind_or_none(state)
    counts = creature_counts(state)
    if winner is not None:
        print(f"Winner: {winner.value} at tick {state.tick}")
        return winner

    print(
        "No winner after "
        f"{max_ticks} ticks. "
        f"rock={counts[CreatureType.ROCK]} "
        f"paper={counts[CreatureType.PAPER]} "
        f"scissors={counts[CreatureType.SCISSORS]}"
    )
    return None
