from dataclasses import dataclass

from .board import Position
from .rps import CreatureType


@dataclass(frozen=True)
class Creature:
    id: int
    kind: CreatureType
    pos: Position
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 0.0
    mass: float = 1.0
