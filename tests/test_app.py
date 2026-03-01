from sim.app import (
    _adjust_menu_value,
    _click_hits_restart,
    _restart_button_rect,
    _toggle_menu_value,
    run_headless,
    winner_kind_or_none,
)
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


def test_adjust_menu_value_changes_numeric_fields() -> None:
    config = SimConfig(
        creature_count=20,
        obstacle_count=2,
        obstacle_avg_size=40.0,
        creature_mass=20.0,
    )

    updated = _adjust_menu_value(config, "creature_count", 10)
    updated = _adjust_menu_value(updated, "obstacle_count", -1)
    updated = _adjust_menu_value(updated, "obstacle_avg_size", 8.0)
    updated = _adjust_menu_value(updated, "creature_mass", 2.0)

    assert updated.creature_count == 30
    assert updated.obstacle_count == 1
    assert updated.obstacle_avg_size == 48.0
    assert updated.creature_mass == 22.0


def test_toggle_menu_value_flips_boolean_fields() -> None:
    config = SimConfig(
        bounce_off_creatures=True,
        convert_loser_to_winner=True,
        grow_on_win=False,
    )

    updated = _toggle_menu_value(config, "bounce_off_creatures")
    updated = _toggle_menu_value(updated, "convert_loser_to_winner")
    updated = _toggle_menu_value(updated, "grow_on_win")

    assert updated.bounce_off_creatures is False
    assert updated.convert_loser_to_winner is False
    assert updated.grow_on_win is True


def test_restart_button_rect_stays_in_top_right() -> None:
    rect = _restart_button_rect(640)

    assert rect == (492, 8, 140, 34)


def test_click_hits_restart_detects_button_area() -> None:
    assert _click_hits_restart((500, 20), 640) is True
    assert _click_hits_restart((470, 20), 640) is False
