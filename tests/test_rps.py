from sim.rps import CreatureType, rps_winner


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
