from datetime import datetime
from dataclasses import replace
from pathlib import Path
import random

from .config import SimConfig
from .game import create_game, creature_counts, step_game
from .rps import RULESETS, CreatureType, battle_rules_for


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
    if field_name == "winner_growth_percent":
        return replace(
            config,
            winner_growth_percent=max(0.0, config.winner_growth_percent + float(delta)),
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
    if field_name == "custom_outcome_enabled":
        return replace(config, custom_outcome_enabled=not config.custom_outcome_enabled)
    raise ValueError(f"Unknown menu field: {field_name}")


def _cycle_menu_value(config: SimConfig, field_name: str) -> SimConfig:
    if field_name == "battle_rule_set":
        rule_names = sorted(RULESETS)
        current_index = rule_names.index(config.battle_rule_set)
        next_index = (current_index + 1) % len(rule_names)
        return replace(config, battle_rule_set=rule_names[next_index])
    if field_name == "terrain_zone_mode":
        terrain_modes = ["off", "mud", "ice", "mixed"]
        current_index = terrain_modes.index(config.terrain_zone_mode)
        next_index = (current_index + 1) % len(terrain_modes)
        return replace(config, terrain_zone_mode=terrain_modes[next_index])
    raise ValueError(f"Unknown menu field: {field_name}")


def _clamp_scroll_offset(offset: int, viewport_height: int, content_height: int) -> int:
    max_offset = max(0, content_height - viewport_height)
    return max(0, min(offset, max_offset))


def _scrollbar_thumb_rect(track_rect, viewport_height: int, content_height: int, scroll_offset: int):
    import pygame

    if content_height <= viewport_height:
        return pygame.Rect(track_rect.x, track_rect.y, track_rect.width, track_rect.height)

    thumb_height = max(36, int(round(track_rect.height * (viewport_height / content_height))))
    max_offset = content_height - viewport_height
    travel = track_rect.height - thumb_height
    thumb_y = track_rect.y + int(round((scroll_offset / max_offset) * travel))
    return pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_height)


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
    scroll_offset = 0
    scroll_step = 56

    def draw_button(rect: pygame.Rect, label: str, hovered: bool, color) -> None:
        fill = hover_color if hovered else color
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, outline_color, rect, 2, border_radius=10)
        text_surface = body_font.render(label, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    rows = [
        ("Creatures", lambda c: str(c.creature_count), "creature_count", 10),
        ("Obstacle Count", lambda c: str(c.obstacle_count), "obstacle_count", 1),
        ("Obstacle Avg Size", lambda c: f"{c.obstacle_avg_size:.0f}", "obstacle_avg_size", 8.0),
        ("Creature Mass", lambda c: f"{c.creature_mass:.0f}", "creature_mass", 2.0),
        ("Creature Speed", lambda c: f"{c.creature_speed:.0f}", "creature_speed", 5.0),
        (
            "Growth Percent",
            lambda c: f"{c.winner_growth_percent:.0f}%",
            "winner_growth_percent",
            10.0,
        ),
    ]
    toggle_rows = [
        ("Creature Bounce", lambda c: "ON" if c.bounce_off_creatures else "OFF", "bounce_off_creatures"),
        (
            "Convert Loser",
            lambda c: "ON" if c.convert_loser_to_winner else "OFF",
            "convert_loser_to_winner",
        ),
        ("Grow On Win", lambda c: "ON" if c.grow_on_win else "OFF", "grow_on_win"),
        (
            "Bigger Wins",
            lambda c: "ON" if c.custom_outcome_enabled else "OFF",
            "custom_outcome_enabled",
        ),
        ("Battle Rules", lambda c: c.battle_rule_set.title(), "battle_rule_set"),
        ("Terrain Zones", lambda c: c.terrain_zone_mode.title(), "terrain_zone_mode"),
    ]

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
        row_gap = 62
        content_top = panel.top + 120
        option_label_x = panel.left + 44
        button_right = panel.right - 132
        button_y_offset = 4
        start_rect = pygame.Rect(panel.left + 30, panel.bottom - 72, 240, 48)
        viewport_rect = pygame.Rect(
            panel.left + 24,
            content_top,
            panel.width - 84,
            max(100, start_rect.top - content_top - 18),
        )
        scrollbar_track = pygame.Rect(panel.right - 34, viewport_rect.top, 10, viewport_rect.height)
        content_height = (len(rows) + len(toggle_rows)) * row_gap
        scroll_offset = _clamp_scroll_offset(scroll_offset, viewport_rect.height, content_height)

        previous_clip = screen.get_clip()
        screen.set_clip(viewport_rect)
        row_y = content_top - scroll_offset

        for label, value_fn, field_name, step in rows:
            if row_y + 42 >= viewport_rect.top and row_y <= viewport_rect.bottom:
                label_surface = body_font.render(
                    f"{label}: {value_fn(current_config)}",
                    True,
                    text_color,
                )
                screen.blit(label_surface, (option_label_x, row_y + 10))

                minus_rect = pygame.Rect(button_right - 68, row_y + button_y_offset, 56, 42)
                plus_rect = pygame.Rect(button_right, row_y + button_y_offset, 56, 42)
                draw_button(minus_rect, "-", minus_rect.collidepoint(mouse_pos), button_color)
                draw_button(plus_rect, "+", plus_rect.collidepoint(mouse_pos), button_color)
                buttons.append((minus_rect, ("adjust", field_name, -step)))
                buttons.append((plus_rect, ("adjust", field_name, step)))
            row_y += row_gap

        for label, value_fn, field_name in toggle_rows:
            if row_y + 42 >= viewport_rect.top and row_y <= viewport_rect.bottom:
                label_surface = body_font.render(
                    f"{label}: {value_fn(current_config)}",
                    True,
                    text_color,
                )
                screen.blit(label_surface, (option_label_x, row_y + 10))
                toggle_rect = pygame.Rect(button_right - 68, row_y + button_y_offset, 124, 42)
                toggle_label = (
                    "Next"
                    if field_name in {"battle_rule_set", "terrain_zone_mode"}
                    else "Toggle"
                )
                draw_button(
                    toggle_rect,
                    toggle_label,
                    toggle_rect.collidepoint(mouse_pos),
                    button_color,
                )
                action_type = (
                    "cycle"
                    if field_name in {"battle_rule_set", "terrain_zone_mode"}
                    else "toggle"
                )
                buttons.append((toggle_rect, (action_type, field_name, None)))
            row_y += row_gap

        screen.set_clip(previous_clip)

        pygame.draw.rect(screen, outline_color, viewport_rect, 2, border_radius=12)
        pygame.draw.rect(screen, (229, 219, 202), scrollbar_track, border_radius=6)
        thumb_rect = _scrollbar_thumb_rect(
            scrollbar_track,
            viewport_rect.height,
            content_height,
            scroll_offset,
        )
        pygame.draw.rect(screen, button_color, thumb_rect, border_radius=6)
        pygame.draw.rect(screen, outline_color, thumb_rect, 2, border_radius=6)

        draw_button(
            start_rect,
            "Start Simulation",
            start_rect.collidepoint(mouse_pos),
            start_color,
        )
        buttons.append((start_rect, ("start", "", None)))

        tip_surface = small_font.render(
            "Use the mouse wheel to scroll the options.",
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
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset = _clamp_scroll_offset(
                    scroll_offset - (event.y * scroll_step),
                    viewport_rect.height,
                    content_height,
                )
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
                    elif action_type == "cycle":
                        current_config = _cycle_menu_value(current_config, field_name)
                    break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in {4, 5}:
                direction = 1 if event.button == 5 else -1
                scroll_offset = _clamp_scroll_offset(
                    scroll_offset + (direction * scroll_step),
                    viewport_rect.height,
                    content_height,
                )

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
        show_debug_overlays = False
        winner = winner_kind_or_none(state)
        winner_announced = False
        draw_state(
            screen,
            state,
            config,
            show_debug_boundaries=show_debug_overlays,
            show_mass_labels=show_debug_overlays,
        )
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
                        show_debug_overlays = not show_debug_overlays
                        state_label = "on" if show_debug_overlays else "off"
                        print(f"Debug overlays {state_label}")
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
                    winner_growth_percent=config.winner_growth_percent,
                    custom_outcome_enabled=config.custom_outcome_enabled,
                    encounter_distance=config.creature_radius * 2,
                    dt_seconds=dt_seconds * speed_multiplier * config.tps_multiplier,
                    battle_rules=battle_rules_for(config.battle_rule_set),
                )
                winner = winner_kind_or_none(state)
                if winner is not None and not winner_announced:
                    print(f"Winner: {winner.value} at tick {state.tick}")
                    winner_announced = True
            draw_state(
                screen,
                state,
                config,
                show_debug_boundaries=show_debug_overlays,
                show_mass_labels=show_debug_overlays,
            )
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
            winner_growth_percent=config.winner_growth_percent,
            custom_outcome_enabled=config.custom_outcome_enabled,
            encounter_distance=config.creature_radius * 2,
            dt_seconds=dt_seconds * config.tps_multiplier,
            battle_rules=battle_rules_for(config.battle_rule_set),
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
