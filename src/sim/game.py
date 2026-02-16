import math
import random
from collections import Counter
from dataclasses import dataclass, field

from .board import Board, Position
from .config import SimConfig
from .creature import Creature
from .rps import CreatureType, rps_winner


@dataclass
class GameState:
    board: Board
    creatures: list[Creature]
    tick: int = 0
    active_collision_pairs: set[tuple[int, int]] = field(default_factory=set)


def _spawn_creature(
    rng: random.Random, board: Board, creature_id: int, creature_speed: float
) -> Creature:
    kind = rng.choice([CreatureType.ROCK, CreatureType.PAPER, CreatureType.SCISSORS])
    pos = Position(rng.uniform(0, board.width), rng.uniform(0, board.height))
    angle = rng.uniform(0.0, math.tau)
    vx = math.cos(angle) * creature_speed
    vy = math.sin(angle) * creature_speed
    return Creature(id=creature_id, kind=kind, pos=pos, vx=vx, vy=vy)


def create_game(config: SimConfig) -> GameState:
    rng = random.Random(config.random_seed)
    board = Board(width=config.window_width, height=config.window_height)
    creatures = [
        _spawn_creature(rng, board, i, config.creature_speed)
        for i in range(config.creature_count)
    ]
    creatures = randomize_creature_speeds(
        creatures=creatures,
        rng=rng,
        min_speed=config.creature_speed * config.min_speed_multiplier,
        max_speed=config.creature_speed * config.max_speed_multiplier,
    )
    return GameState(board=board, creatures=creatures)


def randomize_creature_speeds(
    creatures: list[Creature],
    rng: random.Random,
    min_speed: float,
    max_speed: float,
) -> list[Creature]:
    updated_creatures = []
    for creature in creatures:
        v = rng.uniform(min_speed, max_speed)
        angle = math.atan2(creature.vy, creature.vx)
        new_vx = math.cos(angle) * v
        new_vy = math.sin(angle) * v
        new_creature = Creature(
            id=creature.id,
            kind=creature.kind,
            pos=creature.pos,
            vx=new_vx,
            vy=new_vy,
        )
        updated_creatures.append(new_creature)
    return updated_creatures


def _move_creature(creature: Creature, board: Board, dt_seconds: float) -> Creature:
    next_x = creature.pos.x + (creature.vx * dt_seconds)
    next_y = creature.pos.y + (creature.vy * dt_seconds)
    next_vx = creature.vx
    next_vy = creature.vy

    if next_x < 0 or next_x > board.width:
        next_vx = -next_vx
        next_x = max(0.0, min(board.width, next_x))

    if next_y < 0 or next_y > board.height:
        next_vy = -next_vy
        next_y = max(0.0, min(board.height, next_y))

    return Creature(
        id=creature.id,
        kind=creature.kind,
        pos=Position(next_x, next_y),
        vx=next_vx,
        vy=next_vy,
    )


def _within_distance(a: Creature, b: Creature, distance: float) -> bool:
    dx = a.pos.x - b.pos.x
    dy = a.pos.y - b.pos.y
    return (dx * dx) + (dy * dy) <= distance * distance


def _pair_key(left_id: int, right_id: int) -> tuple[int, int]:
    return (left_id, right_id) if left_id < right_id else (right_id, left_id)


def mirror_vector(
    mx: float,
    my: float,
    x: float,
    y: float,
) -> tuple[float, float]:
    mirror_len_sq = (mx * mx) + (my * my)
    if mirror_len_sq == 0.0:
        return x, y

    scale = ((x * mx) + (y * my)) / mirror_len_sq
    parallel_x = scale * mx
    parallel_y = scale * my
    return (2.0 * parallel_x) - x, (2.0 * parallel_y) - y


def bounce_velocity(
    left_creature: Creature,
    right_creature: Creature,
) -> tuple[tuple[float, float], tuple[float, float]]:
    mx = left_creature.pos.x - right_creature.pos.x
    my = left_creature.pos.y - right_creature.pos.y
    new_vleft = mirror_vector(mx, my, left_creature.vx, left_creature.vy)
    new_vright = mirror_vector(mx, my, right_creature.vx, right_creature.vy)
    new_vleft = -new_vleft[0], -new_vleft[1]
    new_vright = -new_vright[0], -new_vright[1]
    return (new_vleft, new_vright)
    # TODO(Jonah): implement collision bounce math here.
    #return (left_creature.vx, left_creature.vy), (right_creature.vx, right_creature.vy)
    #return (-left_creature.vx, -left_creature.vy), (-right_creature.vx, -right_creature.vy)
    #return (-right_creature.vx, -right_creature.vy), (-left_creature.vx, -left_creature.vy)
    #return (right_creature.vx, right_creature.vy), (left_creature.vx, left_creature.vy)


def step_game(
    state: GameState,
    rng: random.Random,
    convert_loser_to_winner: bool = True,
    encounter_distance: float = 16.0,
    dt_seconds: float = 1.0,
) -> GameState:
    del rng  # Kept in signature so the app can still pass one RNG object.
    moved_creatures: list[Creature] = []

    for creature in state.creatures:
        moved_creatures.append(_move_creature(creature, state.board, dt_seconds))

    by_id: dict[int, Creature] = {c.id: c for c in moved_creatures}
    creature_ids = sorted(by_id.keys())

    if not convert_loser_to_winner:
        collisions_this_tick: set[tuple[int, int]] = set()
        alive_ids = set(creature_ids)
        for left_index, left_id in enumerate(creature_ids):
            if left_id not in alive_ids:
                continue
            for right_id in creature_ids[left_index + 1 :]:
                if right_id not in alive_ids:
                    continue
                left = by_id[left_id]
                right = by_id[right_id]
                if not _within_distance(left, right, encounter_distance):
                    continue

                pair = _pair_key(left_id, right_id)
                collisions_this_tick.add(pair)
                if pair not in state.active_collision_pairs:
                    (next_left_vx, next_left_vy), (next_right_vx, next_right_vy) = (
                        bounce_velocity(
                            left,
                            right,
                        )
                    )
                    by_id[left_id] = Creature(
                        id=left.id,
                        kind=left.kind,
                        pos=left.pos,
                        vx=next_left_vx,
                        vy=next_left_vy,
                    )
                    by_id[right_id] = Creature(
                        id=right.id,
                        kind=right.kind,
                        pos=right.pos,
                        vx=next_right_vx,
                        vy=next_right_vy,
                    )

                winner = rps_winner(left.kind, right.kind)
                if winner is None:
                    continue
                if winner == left.kind:
                    alive_ids.discard(right_id)
                else:
                    alive_ids.discard(left_id)
                    break

        return GameState(
            board=state.board,
            creatures=sorted(
                [by_id[c.id] for c in moved_creatures if c.id in alive_ids],
                key=lambda c: c.id,
            ),
            tick=state.tick + 1,
            active_collision_pairs=collisions_this_tick,
        )

    collisions_this_tick: set[tuple[int, int]] = set()
    kinds_by_id: dict[int, CreatureType] = {c.id: c.kind for c in moved_creatures}

    for left_index, left_id in enumerate(creature_ids):
        for right_id in creature_ids[left_index + 1 :]:
            left = by_id[left_id]
            right = by_id[right_id]
            if not _within_distance(left, right, encounter_distance):
                continue

            pair = _pair_key(left_id, right_id)
            collisions_this_tick.add(pair)
            if pair not in state.active_collision_pairs:
                (next_left_vx, next_left_vy), (next_right_vx, next_right_vy) = (
                    bounce_velocity(
                        left,
                        right,
                    )
                )
                by_id[left_id] = Creature(
                    id=left.id,
                    kind=left.kind,
                    pos=left.pos,
                    vx=next_left_vx,
                    vy=next_left_vy,
                )
                by_id[right_id] = Creature(
                    id=right.id,
                    kind=right.kind,
                    pos=right.pos,
                    vx=next_right_vx,
                    vy=next_right_vy,
                )

            left_kind = kinds_by_id[left_id]
            right_kind = kinds_by_id[right_id]
            winner = rps_winner(left_kind, right_kind)
            if winner is None:
                continue

            if winner == left_kind:
                kinds_by_id[right_id] = left_kind
            else:
                kinds_by_id[left_id] = right_kind

    resolved = [
        Creature(
            id=creature.id,
            kind=kinds_by_id[creature.id],
            pos=by_id[creature.id].pos,
            vx=by_id[creature.id].vx,
            vy=by_id[creature.id].vy,
        )
        for creature in moved_creatures
    ]

    return GameState(
        board=state.board,
        creatures=sorted(resolved, key=lambda c: c.id),
        tick=state.tick + 1,
        active_collision_pairs=collisions_this_tick,
    )


def creature_counts(state: GameState) -> Counter[CreatureType]:
    return Counter(c.kind for c in state.creatures)
