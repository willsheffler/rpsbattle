from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x: float
    y: float


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
