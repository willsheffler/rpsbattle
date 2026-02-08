from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x: int
    y: int


@dataclass(frozen=True)
class Board:
    width: int
    height: int

    def in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def clamp(self, pos: Position) -> Position:
        x = max(0, min(self.width - 1, pos.x))
        y = max(0, min(self.height - 1, pos.y))
        return Position(x, y)
