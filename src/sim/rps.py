from dataclasses import dataclass
from enum import StrEnum


class CreatureType(StrEnum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


@dataclass(frozen=True)
class BattleRules:
    name: str
    wins: dict[CreatureType, CreatureType]

    def winner(self, a: CreatureType, b: CreatureType) -> CreatureType | None:
        """Return winning type, or None for a tie."""
        if a == b:
            return None
        return a if self.wins[a] == b else b


CLASSIC_RULES = BattleRules(
    name="classic",
    wins={
        CreatureType.ROCK: CreatureType.SCISSORS,
        CreatureType.PAPER: CreatureType.ROCK,
        CreatureType.SCISSORS: CreatureType.PAPER,
    },
)

REVERSE_RULES = BattleRules(
    name="reverse",
    wins={
        CreatureType.ROCK: CreatureType.PAPER,
        CreatureType.PAPER: CreatureType.SCISSORS,
        CreatureType.SCISSORS: CreatureType.ROCK,
    },
)

RULESETS: dict[str, BattleRules] = {
    CLASSIC_RULES.name: CLASSIC_RULES,
    REVERSE_RULES.name: REVERSE_RULES,
}


def battle_rules_for(name: str) -> BattleRules:
    try:
        return RULESETS[name]
    except KeyError as exc:
        available = ", ".join(sorted(RULESETS))
        raise ValueError(f"Unknown battle rule set '{name}'. Choose from: {available}") from exc


def rps_winner(
    a: CreatureType,
    b: CreatureType,
    rules: BattleRules = CLASSIC_RULES,
) -> CreatureType | None:
    return rules.winner(a, b)
