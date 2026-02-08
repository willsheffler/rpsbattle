import argparse

from .config import SimConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the RPS creature simulation.")
    parser.add_argument("--width", type=int, default=40, help="Board width in cells.")
    parser.add_argument("--height", type=int, default=30, help="Board height in cells.")
    parser.add_argument("--cell-size", type=int, default=32, help="Size of each cell in pixels.")
    parser.add_argument("--fps", type=int, default=120, help="Frames per second.")
    parser.add_argument("--count", type=int, default=100, help="Number of creatures.")
    parser.add_argument(
        "--speed",
        type=float,
        default=40.0,
        help="Base creature speed in pixels per second.",
    )
    parser.add_argument(
        "--min-speed-mult",
        type=float,
        default=0.3,
        help="Minimum speed multiplier for spawn randomization.",
    )
    parser.add_argument(
        "--max-speed-mult",
        type=float,
        default=3,
        help="Maximum speed multiplier for spawn randomization.",
    )
    parser.add_argument(
        "--tps-multiplier",
        type=float,
        default=1.0,
        help="Global ticks-per-second multiplier for simulation speed.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (default: random each run).",
    )
    parser.add_argument(
        "--no-convert",
        action="store_true",
        help="Disable loser conversion during encounters.",
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
    if args.tps_multiplier <= 0:
        parser.error("--tps-multiplier must be greater than 0")

    from .app import run, run_headless

    config = SimConfig(
        board_width=args.width,
        board_height=args.height,
        cell_size=args.cell_size,
        fps=args.fps,
        creature_count=args.count,
        creature_speed=args.speed,
        min_speed_multiplier=args.min_speed_mult,
        max_speed_multiplier=args.max_speed_mult,
        tps_multiplier=args.tps_multiplier,
        random_seed=args.seed,
        convert_loser_to_winner=not args.no_convert,
    )
    if args.headless:
        run_headless(config, max_ticks=args.max_ticks, dt_seconds=args.headless_dt)
        return

    run(config)
