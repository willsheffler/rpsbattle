from dataclasses import dataclass


@dataclass(frozen=True)
class SimConfig:
    board_width: int = 40
    board_height: int = 30
    cell_size: int = 32
    fps: int = 60
    creature_count: int = 100
    random_seed: int | None = None
    convert_loser_to_winner: bool = True
    creature_radius: int = 20
    creature_mass: float = 1
    creature_speed: float = 40.0
    min_speed_multiplier: float = 0.3
    max_speed_multiplier: float = 3
    tps_multiplier: float = 1.0
    bounce_off_creatures: bool = True
    obstacle_count: int = 7
    obstacle_avg_size: float = 40.0
    grow_on_win: bool = False

    @property
    def window_width(self) -> int:
        return self.board_width * self.cell_size

    @property
    def window_height(self) -> int:
        return self.board_height * self.cell_size
