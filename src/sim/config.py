from dataclasses import dataclass


@dataclass(frozen=True)
class SimConfig:
    board_width: int = 20
    board_height: int = 15
    cell_size: int = 32
    fps: int = 8
    creature_count: int = 10
    random_seed: int = 7

    @property
    def window_width(self) -> int:
        return self.board_width * self.cell_size

    @property
    def window_height(self) -> int:
        return self.board_height * self.cell_size
