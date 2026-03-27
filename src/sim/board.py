from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Position:
    x: float
    y: float


@dataclass(frozen=True)
class Obstacle:
    kind: str
    pos: Position
    size: float
    rotation: float
    color: tuple[int, int, int]

    @property
    def collision_radius(self) -> float:
        return self.size


@dataclass(frozen=True)
class TerrainZone:
    kind: str
    pos: Position
    width: float
    height: float
    speed_multiplier: float
    color: tuple[int, int, int]
    warp_amount: float = 0.18
    warp_phase: float = 0.0

    @property
    def center(self) -> Position:
        return Position(
            self.pos.x + (self.width / 2.0),
            self.pos.y + (self.height / 2.0),
        )

    def radius_scale_at_angle(self, angle: float) -> float:
        wave_a = math.sin((angle * 3.0) + self.warp_phase)
        wave_b = math.cos((angle * 5.0) - (self.warp_phase * 0.7))
        return max(0.65, 1.0 + (self.warp_amount * 0.6 * wave_a) + (self.warp_amount * 0.4 * wave_b))

    def contains(self, pos: Position) -> bool:
        center = self.center
        dx = pos.x - center.x
        dy = pos.y - center.y
        if dx == 0.0 and dy == 0.0:
            return True

        angle = math.atan2(dy, dx)
        scale = self.radius_scale_at_angle(angle)
        rx = max(1.0, (self.width / 2.0) * scale)
        ry = max(1.0, (self.height / 2.0) * scale)
        return ((dx * dx) / (rx * rx)) + ((dy * dy) / (ry * ry)) <= 1.0


@dataclass(frozen=True)
class Board:
    width: float
    height: float

    def in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.x <= self.width and 0 <= pos.y <= self.height

    def clamp(self, pos: Position) -> Position:
        x = max(0.0, min(self.width, pos.x))
        y = max(0.0, min(self.height, pos.y))
        return Position(x, y)
