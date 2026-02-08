import random
from collections import Counter, defaultdict
from dataclasses import dataclass

from .board import Board, Position
from .config import SimConfig
from .creature import Creature
from .rps import CreatureType, rps_winner

_MOVE_DELTAS = [
    Position(0, 0),
    Position(1, 0),
    Position(-1, 0),
    Position(0, 1),
    Position(0, -1),
]


@dataclass
class GameState:
    board: Board
    creatures: list[Creature]
    tick: int = 0


def _spawn_creature(rng: random.Random, board: Board, creature_id: int) -> Creature:
    kind = rng.choice([CreatureType.ROCK, CreatureType.PAPER, CreatureType.SCISSORS])
    pos = Position(rng.randrange(board.width), rng.randrange(board.height))
    return Creature(id=creature_id, kind=kind, pos=pos)


def create_game(config: SimConfig) -> GameState:
    rng = random.Random(config.random_seed)
    board = Board(width=config.board_width, height=config.board_height)
    creatures = [_spawn_creature(rng, board, i) for i in range(config.creature_count)]
    return GameState(board=board, creatures=creatures)


def step_game(state: GameState, rng: random.Random) -> GameState:
    moved_creatures: list[Creature] = []

    for creature in state.creatures:
        delta = rng.choice(_MOVE_DELTAS)
        next_pos = Position(creature.pos.x + delta.x, creature.pos.y + delta.y)
        moved_creatures.append(
            Creature(id=creature.id, kind=creature.kind, pos=state.board.clamp(next_pos))
        )

    by_pos: dict[Position, list[Creature]] = defaultdict(list)
    for creature in moved_creatures:
        by_pos[creature.pos].append(creature)

    resolved: list[Creature] = []
    for group in by_pos.values():
        if len(group) == 1:
            resolved.append(group[0])
            continue

        winner_kind = group[0].kind
        for creature in group[1:]:
            result = rps_winner(winner_kind, creature.kind)
            if result is not None:
                winner_kind = result

        for creature in group:
            resolved.append(Creature(id=creature.id, kind=winner_kind, pos=creature.pos))

    return GameState(board=state.board, creatures=sorted(resolved, key=lambda c: c.id), tick=state.tick + 1)


def creature_counts(state: GameState) -> Counter[CreatureType]:
    return Counter(c.kind for c in state.creatures)
