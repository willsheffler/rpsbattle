import argparse

from .config import SimConfig


def build_parser() -> argparse.ArgumentParser:
    defaults = SimConfig()
    parser = argparse.ArgumentParser(description="Run the RPS creature simulation.")
    parser.add_argument("--width", type=int, default=defaults.board_width, help="Board width in cells.")
    parser.add_argument("--height", type=int, default=defaults.board_height, help="Board height in cells.")
    parser.add_argument("--cell-size", type=int, default=defaults.cell_size, help="Size of each cell in pixels.")
    parser.add_argument("--fps", type=int, default=defaults.fps, help="Frames per second.")
    parser.add_argument("--count", type=int, default=defaults.creature_count, help="Number of creatures.")
    parser.add_argument(
        "--speed",
        type=float,
        default=defaults.creature_speed,
        help="Base creature speed in pixels per second.",
    )
    parser.add_argument(
        "--mass",
        type=float,
        default=defaults.creature_mass,
        help="Starting mass for each creature.",
    )
    parser.add_argument(
        "--min-speed-mult",
        type=float,
        default=defaults.min_speed_multiplier,
        help="Minimum speed multiplier for spawn randomization.",
    )
    parser.add_argument(
        "--max-speed-mult",
        type=float,
        default=defaults.max_speed_multiplier,
        help="Maximum speed multiplier for spawn randomization.",
    )
    parser.add_argument(
        "--tps-multiplier",
        type=float,
        default=defaults.tps_multiplier,
        help="Global ticks-per-second multiplier for simulation speed.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=defaults.random_seed,
        help="Random seed (default: random each run).",
    )
    parser.add_argument(
        "--no-convert",
        action="store_true",
        help="Disable loser conversion during encounters.",
    )
    parser.add_argument(
        "--no-bounce",
        action="store_true",
        help="Disable creature-to-creature bounce on contact.",
    )
    parser.add_argument(
        "--obstacle-count",
        type=int,
        default=defaults.obstacle_count,
        help="Number of obstacles to spawn at game start.",
    )
    parser.add_argument(
        "--obstacle-avg-size",
        type=float,
        default=defaults.obstacle_avg_size,
        help="Average obstacle size in pixels. Actual obstacles vary around this.",
    )
    parser.add_argument(
        "--obstacle-radius",
        dest="obstacle_avg_size",
        type=float,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--grow-on-win",
        action="store_true",
        help="Make creatures grow by the loser's mass when they win or convert another creature.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run simulation without graphics and print winner.",
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=10_000,
        help="Maximum ticks to run in headless mode.",
    )
    parser.add_argument(
        "--headless-dt",
        type=float,
        default=1.0 / 60.0,
        help="Seconds per tick in headless mode.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.min_speed_mult > args.max_speed_mult:
        parser.error("--min-speed-mult must be less than or equal to --max-speed-mult")
    if args.mass <= 0:
        parser.error("--mass must be greater than 0")
    if args.tps_multiplier <= 0:
        parser.error("--tps-multiplier must be greater than 0")
    if args.obstacle_count < 0:
        parser.error("--obstacle-count must be greater than or equal to 0")
    if args.obstacle_avg_size < 0:
        parser.error("--obstacle-avg-size must be greater than or equal to 0")

    from .app import run, run_headless

    config = SimConfig(
        board_width=args.width,
        board_height=args.height,
        cell_size=args.cell_size,
        fps=args.fps,
        creature_count=args.count,
        creature_mass=args.mass,
        creature_speed=args.speed,
        min_speed_multiplier=args.min_speed_mult,
        max_speed_multiplier=args.max_speed_mult,
        tps_multiplier=args.tps_multiplier,
        random_seed=args.seed,
        convert_loser_to_winner=not args.no_convert,
        bounce_off_creatures=not args.no_bounce,
        obstacle_count=args.obstacle_count,
        obstacle_avg_size=args.obstacle_avg_size,
        grow_on_win=args.grow_on_win,
    )
    if args.headless:
        run_headless(config, max_ticks=args.max_ticks, dt_seconds=args.headless_dt)
        return

    run(config)
