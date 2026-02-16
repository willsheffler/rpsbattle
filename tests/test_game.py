import random
import math

import pytest
from sim.board import Board, Position
from sim.creature import Creature
from sim.game import (
    GameState,
    creature_counts,
    mirror_vector,
    randomize_creature_speeds,
    step_game,
)
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


def test_mirror_vector_reflects_across_axis() -> None:
    mirrored_x, mirrored_y = mirror_vector(mx=0.0, my=1.0, x=3.0, y=4.0)

    assert mirrored_x == pytest.approx(-3.0)
    assert mirrored_y == pytest.approx(4.0)


def test_creature_bounces_off_right_wall() -> None:
    state = GameState(
        board=Board(width=5, height=5),
        creatures=[
            Creature(
                id=1,
                kind=CreatureType.ROCK,
                pos=Position(4.5, 2.0),
                vx=1.0,
                vy=0.0,
            )
        ],
        tick=0,
    )

    next_state = step_game(state, random.Random(1), dt_seconds=1.0)
    creature = next_state.creatures[0]

    assert creature.pos.x == 5
    assert creature.vx == -1.0


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


def test_collision_bounces_once_per_contact_and_resets_after_separation() -> None:
    board = Board(width=10, height=10)
    state = GameState(
        board=board,
        creatures=[
            Creature(id=1, kind=CreatureType.ROCK, pos=Position(5, 5), vx=1.0, vy=0.0),
            Creature(id=2, kind=CreatureType.ROCK, pos=Position(5, 5), vx=-2.0, vy=0.0),
        ],
        tick=0,
    )

    first = step_game(state, StubRng(), encounter_distance=1.0, dt_seconds=0.0)
    assert first.creatures[0].vx == -1.0
    assert first.creatures[1].vx == 2.0

    second = step_game(first, StubRng(), encounter_distance=1.0, dt_seconds=0.0)
    assert second.creatures[0].vx == -1.0
    assert second.creatures[1].vx == 2.0
    assert second.active_collision_pairs == {(1, 2)}

    separated_state = GameState(
        board=board,
        creatures=[
            Creature(id=1, kind=CreatureType.ROCK, pos=Position(0, 0), vx=-1.0, vy=0.0),
            Creature(id=2, kind=CreatureType.ROCK, pos=Position(9, 9), vx=2.0, vy=0.0),
        ],
        tick=second.tick,
        active_collision_pairs=second.active_collision_pairs,
    )
    separated = step_game(
        separated_state, StubRng(), encounter_distance=1.0, dt_seconds=0.0
    )
    assert separated.active_collision_pairs == set()

    recollide_state = GameState(
        board=board,
        creatures=[
            Creature(id=1, kind=CreatureType.ROCK, pos=Position(5, 5), vx=-1.0, vy=0.0),
            Creature(id=2, kind=CreatureType.ROCK, pos=Position(5, 5), vx=2.0, vy=0.0),
        ],
        tick=separated.tick,
        active_collision_pairs=separated.active_collision_pairs,
    )
    recollide = step_game(
        recollide_state, StubRng(), encounter_distance=1.0, dt_seconds=0.0
    )
    assert recollide.creatures[0].vx == 1.0
    assert recollide.creatures[1].vx == -2.0


def test_encounter_removes_loser_when_conversion_disabled() -> None:
    state = GameState(
        board=Board(width=3, height=3),
        creatures=[
            Creature(id=1, kind=CreatureType.ROCK, pos=Position(1, 1)),
            Creature(id=2, kind=CreatureType.SCISSORS, pos=Position(1, 1)),
        ],
        tick=0,
    )

    next_state = step_game(state, StubRng(), convert_loser_to_winner=False)

    assert [c.kind for c in next_state.creatures] == [CreatureType.ROCK]


def test_encounter_tie_keeps_both_when_conversion_disabled() -> None:
    state = GameState(
        board=Board(width=3, height=3),
        creatures=[
            Creature(id=1, kind=CreatureType.ROCK, pos=Position(1, 1)),
            Creature(id=2, kind=CreatureType.ROCK, pos=Position(1, 1)),
        ],
        tick=0,
    )

    next_state = step_game(state, StubRng(), convert_loser_to_winner=False)

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


def test_randomize_creature_speeds_changes_speed_and_keeps_direction() -> None:
    creatures = [
        Creature(
            id=1,
            kind=CreatureType.ROCK,
            pos=Position(10.0, 10.0),
            vx=3.0,
            vy=4.0,  # direction angle atan2(4, 3)
        ),
        Creature(
            id=2,
            kind=CreatureType.PAPER,
            pos=Position(20.0, 5.0),
            vx=-4.0,
            vy=3.0,
        ),
    ]

    updated = randomize_creature_speeds(
        creatures=creatures,
        rng=random.Random(123),
        min_speed=2.0,
        max_speed=6.0,
    )

    assert len(updated) == len(creatures)
    any_speed_changed = False
    for original, new in zip(creatures, updated, strict=True):
        assert new.id == original.id
        assert new.kind == original.kind
        assert new.pos == original.pos

        original_speed = math.hypot(original.vx, original.vy)
        new_speed = math.hypot(new.vx, new.vy)
        assert 2.0 <= new_speed <= 6.0
        if not math.isclose(new_speed, original_speed, rel_tol=0.0, abs_tol=1e-9):
            any_speed_changed = True

        original_angle = math.atan2(original.vy, original.vx)
        new_angle = math.atan2(new.vy, new.vx)
        assert new_angle == pytest.approx(original_angle, abs=1e-6)

    assert any_speed_changed
