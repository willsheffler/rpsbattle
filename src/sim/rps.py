from enum import StrEnum


class CreatureType(StrEnum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


def rps_winner(a: CreatureType, b: CreatureType) -> CreatureType | None:
    """Return winning type, or None for a tie."""
    if a == b:
        return None

    wins = {
        (CreatureType.ROCK, CreatureType.SCISSORS),
        (CreatureType.SCISSORS, CreatureType.PAPER),
        (CreatureType.PAPER, CreatureType.ROCK),
    }
    return a if (a, b) in wins else b
