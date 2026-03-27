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
_TEXTURE_DIR = Path("assets/textures")
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


@lru_cache(maxsize=16)
def _load_terrain_texture(kind: str, width: int, height: int) -> pygame.Surface:
    texture_path = _TEXTURE_DIR / f"terrain-{kind}.png"
    texture = pygame.image.load(str(texture_path)).convert_alpha()
    return pygame.transform.smoothscale(texture, (max(1, width), max(1, height)))


def _draw_creatures(screen: pygame.Surface, state: GameState, config: SimConfig) -> None:
    for creature in state.creatures:
        radius = max(1, int(round(creature.radius)))
        sprite = _load_sprite(creature.kind, radius)
        center_x = int(creature.pos.x)
        center_y = int(creature.pos.y)
        top_left = (center_x - radius, center_y - radius)
        screen.blit(sprite, top_left)


def _draw_creature_masses(screen: pygame.Surface, state: GameState) -> None:
    font = pygame.font.Font(None, 20)
    for creature in state.creatures:
        label = str(int(round(creature.mass)))
        text_surface = font.render(label, True, _TEXT_COLOR)
        text_rect = text_surface.get_rect(
            center=(int(round(creature.pos.x)), int(round(creature.pos.y)))
        )
        screen.blit(text_surface, text_rect)


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


def _terrain_points(zone) -> list[tuple[int, int]]:
    center = zone.center
    points: list[tuple[int, int]] = []
    for step in range(24):
        angle = (math.tau * step) / 24.0
        scale = zone.radius_scale_at_angle(angle)
        radius_x = (zone.width / 2.0) * scale
        radius_y = (zone.height / 2.0) * scale
        points.append(
            (
                int(round(center.x + (math.cos(angle) * radius_x))),
                int(round(center.y + (math.sin(angle) * radius_y))),
            )
        )
    return points


def _draw_textured_terrain(surface: pygame.Surface, zone, points: list[tuple[int, int]]) -> None:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    left = min(xs)
    top = min(ys)
    width = max(1, max(xs) - left)
    height = max(1, max(ys) - top)

    local_points = [(x - left, y - top) for x, y in points]
    texture = _load_terrain_texture(zone.kind, width, height).copy()

    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local_points)
    texture.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    tint = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.polygon(tint, (*zone.color, 65), local_points)
    texture.blit(tint, (0, 0))

    surface.blit(texture, (left, top))


def _draw_terrain_zones(screen: pygame.Surface, state: GameState) -> None:
    for zone in state.terrain_zones:
        points = _terrain_points(zone)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        _draw_textured_terrain(overlay, zone, points)
        screen.blit(overlay, (0, 0))
        pygame.draw.polygon(screen, zone.color, points, 3)


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
    show_mass_labels: bool = False,
) -> None:
    screen.fill(_BG_COLOR)
    _draw_terrain_zones(screen, state)
    _draw_obstacles(screen, state)
    _draw_creatures(screen, state, config)
    if show_mass_labels:
        _draw_creature_masses(screen, state)
    if show_debug_boundaries:
        _draw_debug_boundaries(screen, state)
    _draw_hud(screen, state)
