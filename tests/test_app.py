from sim.app import run_headless, winner_kind_or_none
from sim.board import Board, Position
from sim.config import SimConfig
from sim.creature import Creature
from sim.game import GameState
from sim.rps import CreatureType


def test_winner_kind_or_none_returns_winner_when_one_type_left() -> None:
    state = GameState(
        board=Board(width=10, height=10),
        creatures=[
            Creature(id=1, kind=CreatureType.ROCK, pos=Position(1, 1)),
            Creature(id=2, kind=CreatureType.ROCK, pos=Position(2, 2)),
        ],
    )
    assert winner_kind_or_none(state) == CreatureType.ROCK


def test_winner_kind_or_none_returns_none_for_mixed_types() -> None:
    state = GameState(
        board=Board(width=10, height=10),
        creatures=[
            Creature(id=1, kind=CreatureType.ROCK, pos=Position(1, 1)),
            Creature(id=2, kind=CreatureType.PAPER, pos=Position(2, 2)),
        ],
    )
    assert winner_kind_or_none(state) is None


def test_run_headless_prints_no_winner_when_empty_and_zero_ticks(capsys) -> None:
    config = SimConfig(creature_count=0)
    winner = run_headless(config=config, max_ticks=0, dt_seconds=1.0 / 60.0)
    captured = capsys.readouterr()
    assert winner is None
    assert "No winner after 0 ticks" in captured.out


def test_run_headless_prints_winner_with_single_creature(capsys) -> None:
    config = SimConfig(creature_count=1, random_seed=1)
    winner = run_headless(config=config, max_ticks=10, dt_seconds=1.0 / 60.0)
    captured = capsys.readouterr()
    assert winner in {CreatureType.ROCK, CreatureType.PAPER, CreatureType.SCISSORS}
    assert "Winner:" in captured.out
