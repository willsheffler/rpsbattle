from functools import lru_cache
import math
from pathlib import Path

import pygame

from .config import SimConfig
from .game import GameState, _creature_primitives, _obstacle_primitives, creature_counts
from .geometry import Capsule, Circle, Polygon
from .rps import CreatureType

_BG_COLOR = (240, 243, 247)
_COLOR_BY_TYPE = {
    CreatureType.ROCK: (220, 80, 80),
    CreatureType.PAPER: (70, 130, 210),
    CreatureType.SCISSORS: (70, 170, 90),
}
_TEXT_COLOR = (25, 30, 40)
_SPRITE_DIR = Path("assets/sprites")
_DEBUG_CREATURE_COLOR = (255, 140, 60)
_DEBUG_OBSTACLE_COLOR = (80, 20, 20)


def _build_default_sprite(kind: CreatureType, radius: int) -> pygame.Surface:
    diameter = radius * 2
    sprite = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

    if kind == CreatureType.ROCK:
        rock_fill = (150, 155, 165)
        rock_outline = (75, 80, 90)
        points = [
            (radius // 2, radius + radius // 4),
            (radius - radius // 3, radius // 3),
            (radius + radius // 6, radius // 5),
            (radius + radius // 2, radius // 2),
            (radius + radius // 2, radius + radius // 4),
            (radius + radius // 8, diameter - radius // 5),
            (radius - radius // 3, diameter - radius // 4),
        ]
        pygame.draw.polygon(sprite, rock_fill, points)
        pygame.draw.polygon(sprite, rock_outline, points, 2)
        pygame.draw.line(
            sprite,
            rock_outline,
            (radius - radius // 6, radius),
            (radius + radius // 4, radius + radius // 6),
            2,
        )
    elif kind == CreatureType.PAPER:
        pad = max(2, radius // 4)
        page = pygame.Rect(pad, pad, diameter - (2 * pad), diameter - (2 * pad))
        pygame.draw.rect(sprite, (252, 252, 255), page, border_radius=3)
        pygame.draw.rect(sprite, (95, 110, 135), page, 2, border_radius=3)
        fold = [
            (page.right - pad, page.top),
            (page.right, page.top),
            (page.right, page.top + pad),
        ]
        pygame.draw.polygon(sprite, (230, 236, 247), fold)
        for idx in range(3):
            y = page.top + pad + (idx * max(2, radius // 3))
            pygame.draw.line(
                sprite,
                (160, 170, 195),
                (page.left + pad // 2, y),
                (page.right - pad, y),
                1,
            )
    else:
        blade = (220, 228, 240)
        width = max(2, radius // 5)
        pygame.draw.line(
            sprite,
            blade,
            (radius // 3, radius // 3),
            (diameter - radius // 3, diameter - radius // 3),
            width,
        )
        pygame.draw.line(
            sprite,
            blade,
            (radius // 3, diameter - radius // 3),
            (diameter - radius // 3, radius // 3),
            width,
        )
        handle_r = max(2, radius // 4)
        handle_color = (205, 115, 80)
        pygame.draw.circle(
            sprite,
            handle_color,
            (radius - handle_r, radius + radius // 4),
            handle_r,
            2,
        )
        pygame.draw.circle(
            sprite,
            handle_color,
            (radius + handle_r, radius + radius // 4),
            handle_r,
            2,
        )

    return sprite


def _sprite_path(kind: CreatureType) -> Path:
    return _SPRITE_DIR / f"{kind.value}.png"


def _ensure_sprite_assets(radius: int) -> None:
    _SPRITE_DIR.mkdir(parents=True, exist_ok=True)
    for kind in CreatureType:
        path = _sprite_path(kind)
        # Keep default file sprites in sync with current built-in art.
        pygame.image.save(_build_default_sprite(kind, radius), str(path))


@lru_cache(maxsize=32)
def _load_sprite(kind: CreatureType, radius: int) -> pygame.Surface:
    _ensure_sprite_assets(radius)
    sprite = pygame.image.load(str(_sprite_path(kind))).convert_alpha()
    expected_size = radius * 2
    if sprite.get_width() != expected_size or sprite.get_height() != expected_size:
        sprite = pygame.transform.smoothscale(sprite, (expected_size, expected_size))
    return sprite


def _draw_creatures(screen: pygame.Surface, state: GameState, config: SimConfig) -> None:
    for creature in state.creatures:
        radius = max(1, int(round(creature.radius)))
        sprite = _load_sprite(creature.kind, radius)
        center_x = int(creature.pos.x)
        center_y = int(creature.pos.y)
        top_left = (center_x - radius, center_y - radius)
        screen.blit(sprite, top_left)


def _draw_obstacles(screen: pygame.Surface, state: GameState) -> None:
    for obstacle in state.obstacles:
        center = (int(obstacle.pos.x), int(obstacle.pos.y))
        size = max(6, int(round(obstacle.size)))
        fill = obstacle.color
        outline = (70, 75, 85)
        if obstacle.kind == "square":
            points = [
                (-size, -size),
                (size, -size),
                (size, size),
                (-size, size),
            ]
            rotated = []
            cos_angle = math.cos(obstacle.rotation)
            sin_angle = math.sin(obstacle.rotation)
            for x, y in points:
                rx = (x * cos_angle) - (y * sin_angle)
                ry = (x * sin_angle) + (y * cos_angle)
                rotated.append((int(round(center[0] + rx)), int(round(center[1] + ry))))
            pygame.draw.polygon(screen, fill, rotated)
            pygame.draw.polygon(screen, outline, rotated, 3)
        elif obstacle.kind == "triangle":
            points = [
                (0, -size),
                (-size, size),
                (size, size),
            ]
            rotated = []
            cos_angle = math.cos(obstacle.rotation)
            sin_angle = math.sin(obstacle.rotation)
            for x, y in points:
                rx = (x * cos_angle) - (y * sin_angle)
                ry = (x * sin_angle) + (y * cos_angle)
                rotated.append((int(round(center[0] + rx)), int(round(center[1] + ry))))
            pygame.draw.polygon(screen, fill, rotated)
            pygame.draw.polygon(screen, outline, rotated, 3)
        else:
            pygame.draw.circle(screen, fill, center, size)
            pygame.draw.circle(screen, outline, center, size, 3)


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


def _draw_debug_primitive(
    screen: pygame.Surface,
    primitive: Circle | Capsule | Polygon,
    color: tuple[int, int, int],
) -> None:
    if isinstance(primitive, Circle):
        pygame.draw.circle(
            screen,
            color,
            (int(primitive.center.x), int(primitive.center.y)),
            int(round(primitive.radius)),
            1,
        )
        return

    if isinstance(primitive, Capsule):
        start = (int(round(primitive.start.x)), int(round(primitive.start.y)))
        end = (int(round(primitive.end.x)), int(round(primitive.end.y)))
        width = max(1, int(round(primitive.radius * 2)))
        pygame.draw.line(screen, color, start, end, width)
        pygame.draw.circle(screen, color, start, int(round(primitive.radius)), 1)
        pygame.draw.circle(screen, color, end, int(round(primitive.radius)), 1)
        return

    points = [(int(round(vertex.x)), int(round(vertex.y))) for vertex in primitive.vertices]
    pygame.draw.polygon(screen, color, points, 1)


def _draw_debug_boundaries(screen: pygame.Surface, state: GameState) -> None:
    for obstacle in state.obstacles:
        for primitive in _obstacle_primitives(obstacle):
            _draw_debug_primitive(screen, primitive, _DEBUG_OBSTACLE_COLOR)

    for creature in state.creatures:
        for primitive in _creature_primitives(creature):
            _draw_debug_primitive(screen, primitive, _DEBUG_CREATURE_COLOR)


def draw_state(
    screen: pygame.Surface,
    state: GameState,
    config: SimConfig,
    show_debug_boundaries: bool = False,
) -> None:
    screen.fill(_BG_COLOR)
    _draw_obstacles(screen, state)
    _draw_creatures(screen, state, config)
    if show_debug_boundaries:
        _draw_debug_boundaries(screen, state)
    _draw_hud(screen, state)
