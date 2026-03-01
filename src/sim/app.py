from datetime import datetime
from dataclasses import replace
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


def _restart_button_rect(window_width: int) -> tuple[int, int, int, int]:
    return (window_width - 148, 8, 140, 34)


def _click_hits_restart(click_pos: tuple[int, int], window_width: int) -> bool:
    x, y, width, height = _restart_button_rect(window_width)
    click_x, click_y = click_pos
    return x <= click_x <= (x + width) and y <= click_y <= (y + height)


def _adjust_menu_value(config: SimConfig, field_name: str, delta: int | float) -> SimConfig:
    if field_name == "creature_count":
        return replace(
            config,
            creature_count=max(1, config.creature_count + int(delta)),
        )
    if field_name == "obstacle_count":
        return replace(
            config,
            obstacle_count=max(0, config.obstacle_count + int(delta)),
        )
    if field_name == "obstacle_avg_size":
        return replace(
            config,
            obstacle_avg_size=max(0.0, config.obstacle_avg_size + float(delta)),
        )
    if field_name == "creature_mass":
        return replace(
            config,
            creature_mass=max(0.1, config.creature_mass + float(delta)),
        )
    if field_name == "creature_speed":
        return replace(
            config,
            creature_speed=max(1.0, config.creature_speed + float(delta)),
        )
    raise ValueError(f"Unknown menu field: {field_name}")


def _toggle_menu_value(config: SimConfig, field_name: str) -> SimConfig:
    if field_name == "bounce_off_creatures":
        return replace(config, bounce_off_creatures=not config.bounce_off_creatures)
    if field_name == "convert_loser_to_winner":
        return replace(
            config,
            convert_loser_to_winner=not config.convert_loser_to_winner,
        )
    if field_name == "grow_on_win":
        return replace(config, grow_on_win=not config.grow_on_win)
    raise ValueError(f"Unknown menu field: {field_name}")


def _run_start_menu(screen, config: SimConfig) -> SimConfig | None:
    import pygame

    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, 54)
    body_font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)
    bg_color = (244, 239, 230)
    panel_color = (255, 250, 242)
    outline_color = (120, 104, 82)
    text_color = (35, 34, 30)
    button_color = (216, 197, 168)
    start_color = (120, 165, 94)
    hover_color = (232, 214, 187)
    current_config = config

    def draw_button(rect: pygame.Rect, label: str, hovered: bool, color) -> None:
        fill = hover_color if hovered else color
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, outline_color, rect, 2, border_radius=10)
        text_surface = body_font.render(label, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    while True:
        screen.fill(bg_color)
        panel = pygame.Rect(40, 40, screen.get_width() - 80, screen.get_height() - 80)
        pygame.draw.rect(screen, panel_color, panel, border_radius=18)
        pygame.draw.rect(screen, outline_color, panel, 3, border_radius=18)

        title = title_font.render("Choose The Starting Variables", True, text_color)
        screen.blit(title, (panel.left + 30, panel.top + 24))

        subtitle = small_font.render(
            "Click buttons to change values, then press Start Simulation.",
            True,
            text_color,
        )
        screen.blit(subtitle, (panel.left + 30, panel.top + 72))

        mouse_pos = pygame.mouse.get_pos()
        buttons: list[tuple[pygame.Rect, tuple[str, str, int | float | None]]] = []
        row_y = panel.top + 120
        row_gap = 62

        rows = [
            ("Creatures", str(current_config.creature_count), "creature_count", 10),
            ("Obstacle Count", str(current_config.obstacle_count), "obstacle_count", 1),
            (
                "Obstacle Avg Size",
                f"{current_config.obstacle_avg_size:.0f}",
                "obstacle_avg_size",
                8.0,
            ),
            (
                "Creature Mass",
                f"{current_config.creature_mass:.0f}",
                "creature_mass",
                2.0,
            ),
            (
                "Creature Speed",
                f"{current_config.creature_speed:.0f}",
                "creature_speed",
                5.0,
            ),
        ]

        for label, value, field_name, step in rows:
            label_surface = body_font.render(f"{label}: {value}", True, text_color)
            screen.blit(label_surface, (panel.left + 30, row_y + 10))

            minus_rect = pygame.Rect(panel.right - 180, row_y, 56, 42)
            plus_rect = pygame.Rect(panel.right - 112, row_y, 56, 42)
            draw_button(
                minus_rect,
                "-",
                minus_rect.collidepoint(mouse_pos),
                button_color,
            )
            draw_button(
                plus_rect,
                "+",
                plus_rect.collidepoint(mouse_pos),
                button_color,
            )
            buttons.append((minus_rect, ("adjust", field_name, -step)))
            buttons.append((plus_rect, ("adjust", field_name, step)))
            row_y += row_gap

        toggle_rows = [
            (
                "Creature Bounce",
                "ON" if current_config.bounce_off_creatures else "OFF",
                "bounce_off_creatures",
            ),
            (
                "Convert Loser",
                "ON" if current_config.convert_loser_to_winner else "OFF",
                "convert_loser_to_winner",
            ),
            (
                "Grow On Win",
                "ON" if current_config.grow_on_win else "OFF",
                "grow_on_win",
            ),
        ]

        for label, value, field_name in toggle_rows:
            label_surface = body_font.render(f"{label}: {value}", True, text_color)
            screen.blit(label_surface, (panel.left + 30, row_y + 10))
            toggle_rect = pygame.Rect(panel.right - 180, row_y, 124, 42)
            toggle_label = "Toggle"
            draw_button(
                toggle_rect,
                toggle_label,
                toggle_rect.collidepoint(mouse_pos),
                button_color,
            )
            buttons.append((toggle_rect, ("toggle", field_name, None)))
            row_y += row_gap

        start_rect = pygame.Rect(panel.left + 30, panel.bottom - 78, 240, 48)
        draw_button(
            start_rect,
            "Start Simulation",
            start_rect.collidepoint(mouse_pos),
            start_color,
        )
        buttons.append((start_rect, ("start", "", None)))

        tip_surface = small_font.render(
            "Tip: use the CLI for exact values, or use this menu for quick experiments.",
            True,
            text_color,
        )
        screen.blit(tip_surface, (panel.left + 290, panel.bottom - 64))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return current_config
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                file_path = _save_screenshot(screen)
                print(f"Screenshot saved: {file_path}")
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, action in buttons:
                    if not rect.collidepoint(event.pos):
                        continue
                    action_type, field_name, value = action
                    if action_type == "start":
                        return current_config
                    if action_type == "adjust":
                        current_config = _adjust_menu_value(current_config, field_name, value)
                    elif action_type == "toggle":
                        current_config = _toggle_menu_value(current_config, field_name)
                    break

        clock.tick(60)


def _draw_restart_button(screen) -> None:
    import pygame

    x, y, width, height = _restart_button_rect(screen.get_width())
    rect = pygame.Rect(x, y, width, height)
    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)
    fill = (233, 206, 171) if hovered else (220, 190, 152)
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, (120, 104, 82), rect, 2, border_radius=10)
    font = pygame.font.Font(None, 28)
    label = font.render("Restart", True, (35, 34, 30))
    screen.blit(label, label.get_rect(center=rect.center))


def _draw_winner_banner(screen, winner: CreatureType) -> None:
    import pygame

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((18, 18, 18, 110))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(0, 0, min(420, screen.get_width() - 40), 120)
    panel.center = (screen.get_width() // 2, screen.get_height() // 2)
    pygame.draw.rect(screen, (255, 247, 232), panel, border_radius=18)
    pygame.draw.rect(screen, (120, 104, 82), panel, 3, border_radius=18)

    title_font = pygame.font.Font(None, 54)
    body_font = pygame.font.Font(None, 30)
    title = title_font.render(f"{winner.value.title()} wins!", True, (35, 34, 30))
    body = body_font.render("Click Restart to change settings.", True, (35, 34, 30))
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + 40)))
    screen.blit(body, body.get_rect(center=(panel.centerx, panel.top + 82)))


def run(config: SimConfig | None = None) -> None:
    import pygame

    from .render import draw_state

    config = config or SimConfig()
    rng = random.Random(config.random_seed)

    pygame.init()
    screen = pygame.display.set_mode((config.window_width, config.window_height))
    pygame.display.set_caption("RPS Battle")
    clock = pygame.time.Clock()

    app_running = True
    while app_running:
        selected_config = _run_start_menu(screen, config)
        if selected_config is None:
            break
        config = selected_config

        state = create_game(config)
        running = True
        speed_multiplier = 1.0
        screenshot_requested = False
        show_debug_boundaries = False
        winner = winner_kind_or_none(state)
        winner_announced = False
        draw_state(screen, state, config, show_debug_boundaries=show_debug_boundaries)
        if winner is not None:
            _draw_winner_banner(screen, winner)
        _draw_restart_button(screen)
        pygame.display.flip()
        clock.tick(config.fps)

        while running:
            dt_seconds = clock.tick(config.fps) / 1000.0
            restart_requested = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    app_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFTBRACKET:
                        speed_multiplier = max(0.25, speed_multiplier - 0.25)
                        print(f"Speed x{speed_multiplier:.2f}")
                    elif event.key == pygame.K_RIGHTBRACKET:
                        speed_multiplier = min(4.0, speed_multiplier + 0.25)
                        print(f"Speed x{speed_multiplier:.2f}")
                    elif event.key == pygame.K_p:
                        screenshot_requested = True
                    elif event.key == pygame.K_d:
                        show_debug_boundaries = not show_debug_boundaries
                        state_label = "on" if show_debug_boundaries else "off"
                        print(f"Collision debug {state_label}")
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if _click_hits_restart(event.pos, screen.get_width()):
                        restart_requested = True
                        running = False
                        break

            if restart_requested or not app_running:
                continue

            if winner is None:
                state = step_game(
                    state,
                    rng,
                    convert_loser_to_winner=config.convert_loser_to_winner,
                    bounce_off_creatures=config.bounce_off_creatures,
                    grow_on_win=config.grow_on_win,
                    encounter_distance=config.creature_radius * 2,
                    dt_seconds=dt_seconds * speed_multiplier * config.tps_multiplier,
                )
                winner = winner_kind_or_none(state)
                if winner is not None and not winner_announced:
                    print(f"Winner: {winner.value} at tick {state.tick}")
                    winner_announced = True
            draw_state(screen, state, config, show_debug_boundaries=show_debug_boundaries)
            if winner is not None:
                _draw_winner_banner(screen, winner)
            _draw_restart_button(screen)
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
            bounce_off_creatures=config.bounce_off_creatures,
            grow_on_win=config.grow_on_win,
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
