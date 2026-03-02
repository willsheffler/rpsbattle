import pytest

from sim.rps import CreatureType, battle_rules_for, rps_winner


def test_tie_returns_none() -> None:
    assert rps_winner(CreatureType.ROCK, CreatureType.ROCK) is None


def test_winning_pairs() -> None:
    assert rps_winner(CreatureType.ROCK, CreatureType.SCISSORS) == CreatureType.ROCK
    assert rps_winner(CreatureType.SCISSORS, CreatureType.PAPER) == CreatureType.SCISSORS
    assert rps_winner(CreatureType.PAPER, CreatureType.ROCK) == CreatureType.PAPER


def test_losing_pairs() -> None:
    assert rps_winner(CreatureType.SCISSORS, CreatureType.ROCK) == CreatureType.ROCK
    assert rps_winner(CreatureType.PAPER, CreatureType.SCISSORS) == CreatureType.SCISSORS
    assert rps_winner(CreatureType.ROCK, CreatureType.PAPER) == CreatureType.PAPER


def test_reverse_rules_flip_winner() -> None:
    reverse_rules = battle_rules_for("reverse")

    assert (
        rps_winner(CreatureType.ROCK, CreatureType.SCISSORS, reverse_rules)
        == CreatureType.SCISSORS
    )


def test_unknown_rule_set_raises_error() -> None:
    with pytest.raises(ValueError, match="Unknown battle rule set"):
        battle_rules_for("volcano")
