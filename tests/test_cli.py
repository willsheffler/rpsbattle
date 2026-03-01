from sim.cli import build_parser
from sim.config import SimConfig


def test_no_bounce_flag_disables_creature_bounce() -> None:
    parser = build_parser()

    args = parser.parse_args(["--no-bounce"])

    assert args.no_bounce is True


def test_obstacle_options_parse() -> None:
    parser = build_parser()

    args = parser.parse_args(["--obstacle-count", "4", "--obstacle-avg-size", "18"])

    assert args.obstacle_count == 4
    assert args.obstacle_avg_size == 18


def test_growth_options_parse() -> None:
    parser = build_parser()

    args = parser.parse_args(["--grow-on-win"])

    assert args.grow_on_win is True


def test_parser_defaults_come_from_sim_config() -> None:
    parser = build_parser()
    args = parser.parse_args([])
    defaults = SimConfig()

    assert args.width == defaults.board_width
    assert args.height == defaults.board_height
    assert args.cell_size == defaults.cell_size
    assert args.fps == defaults.fps
    assert args.count == defaults.creature_count
    assert args.speed == defaults.creature_speed
    assert args.mass == defaults.creature_mass
    assert args.min_speed_mult == defaults.min_speed_multiplier
    assert args.max_speed_mult == defaults.max_speed_multiplier
    assert args.tps_multiplier == defaults.tps_multiplier
    assert args.obstacle_count == defaults.obstacle_count
    assert args.obstacle_avg_size == defaults.obstacle_avg_size
