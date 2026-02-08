from dataclasses import dataclass


@dataclass(frozen=True)
class SimConfig:
#   TODO: make cli.py respect this
    board_width: int = 40
    board_height: int = 30
    cell_size: int = 32
    fps: int = 60
    creature_count: int = 50
    random_seed: int | None = None
    convert_loser_to_winner: bool = True
    creature_radius: int = 20
    creature_speed: float = 40.0
    min_speed_multiplier: float = 0.3
    max_speed_multiplier: float = 3
    tps_multiplier: float = 1.0

    @property
    def window_width(self) -> int:
        return self.board_width * self.cell_size

    @property
    def window_height(self) -> int:
        return self.board_height * self.cell_size
