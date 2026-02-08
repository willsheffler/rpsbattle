import random

from sim.board import Board, Position
from sim.creature import Creature
from sim.game import GameState, creature_counts, step_game
from sim.rps import CreatureType


class StubRng:
    def choice(self, items):
        return items[0]


def test_step_increments_tick() -> None:
    state = GameState(
        board=Board(width=4, height=4),
        creatures=[Creature(id=1, kind=CreatureType.ROCK, pos=Position(0, 0))],
        tick=0,
    )

    next_state = step_game(state, random.Random(1))

    assert next_state.tick == 1


def test_encounter_resolves_types_on_shared_tile() -> None:
    state = GameState(
        board=Board(width=3, height=3),
        creatures=[
            Creature(id=1, kind=CreatureType.ROCK, pos=Position(1, 1)),
            Creature(id=2, kind=CreatureType.SCISSORS, pos=Position(1, 1)),
        ],
        tick=0,
    )

    next_state = step_game(state, StubRng())

    assert [c.kind for c in next_state.creatures] == [CreatureType.ROCK, CreatureType.ROCK]


def test_creature_counts() -> None:
    state = GameState(
        board=Board(width=2, height=2),
        creatures=[
            Creature(id=1, kind=CreatureType.ROCK, pos=Position(0, 0)),
            Creature(id=2, kind=CreatureType.ROCK, pos=Position(0, 1)),
            Creature(id=3, kind=CreatureType.PAPER, pos=Position(1, 1)),
        ],
    )

    counts = creature_counts(state)

    assert counts[CreatureType.ROCK] == 2
    assert counts[CreatureType.PAPER] == 1
    assert counts[CreatureType.SCISSORS] == 0
