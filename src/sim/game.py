import math
import random
from collections import Counter
from dataclasses import dataclass, field

from .board import Board, Obstacle, Position
from .config import SimConfig
from .creature import Creature
from .geometry import (
    Capsule,
    Circle,
    Polygon,
    capsule_capsule_overlap,
    circle_capsule_overlap,
    circle_circle_overlap,
    circle_polygon_overlap,
    normalize,
    polygon_capsule_overlap,
    polygon_closest_point,
    polygon_polygon_overlap,
    primitive_support_distance,
)
from .rps import CreatureType, rps_winner


@dataclass
class GameState:
    board: Board
    creatures: list[Creature]
    obstacles: list[Obstacle] = field(default_factory=list)
    tick: int = 0
    active_collision_pairs: set[tuple[int, int]] = field(default_factory=set)


def _translate(point: Position, dx: float, dy: float) -> Position:
    return Position(point.x + dx, point.y + dy)


def _rotate(point: Position, angle: float) -> Position:
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    return Position(
        (point.x * cos_angle) - (point.y * sin_angle),
        (point.x * sin_angle) + (point.y * cos_angle),
    )


def _creature_primitives(creature: Creature) -> list[Circle | Capsule | Polygon]:
    return [Circle(center=creature.pos, radius=creature.radius)]


def _creature_primitives_at_origin(kind: CreatureType, radius: float) -> list[Circle | Capsule | Polygon]:
    return _creature_primitives(
        Creature(
            id=0,
            kind=kind,
            pos=Position(0.0, 0.0),
            radius=radius,
            mass=1.0,
        )
    )


def _obstacle_primitives(obstacle: Obstacle) -> list[Circle | Polygon]:
    if obstacle.kind == "square":
        points = (
            Position(-obstacle.size, -obstacle.size),
            Position(obstacle.size, -obstacle.size),
            Position(obstacle.size, obstacle.size),
            Position(-obstacle.size, obstacle.size),
        )
        return [
            Polygon(
                tuple(
                    _translate(_rotate(point, obstacle.rotation), obstacle.pos.x, obstacle.pos.y)
                    for point in points
                )
            )
        ]
    if obstacle.kind == "triangle":
        points = (
            Position(0.0, -obstacle.size),
            Position(-obstacle.size, obstacle.size),
            Position(obstacle.size, obstacle.size),
        )
        return [
            Polygon(
                tuple(
                    _translate(_rotate(point, obstacle.rotation), obstacle.pos.x, obstacle.pos.y)
                    for point in points
                )
            )
        ]
    return [Circle(center=obstacle.pos, radius=obstacle.size)]


def _primitives_overlap(
    left: Circle | Capsule | Polygon,
    right: Circle | Capsule | Polygon,
) -> bool:
    if isinstance(left, Circle) and isinstance(right, Circle):
        return circle_circle_overlap(left, right)
    if isinstance(left, Circle) and isinstance(right, Polygon):
        return circle_polygon_overlap(left, right)
    if isinstance(left, Polygon) and isinstance(right, Circle):
        return circle_polygon_overlap(right, left)
    if isinstance(left, Polygon) and isinstance(right, Polygon):
        return polygon_polygon_overlap(left, right)
    if isinstance(left, Circle) and isinstance(right, Capsule):
        return circle_capsule_overlap(left, right)
    if isinstance(left, Capsule) and isinstance(right, Circle):
        return circle_capsule_overlap(right, left)
    if isinstance(left, Polygon) and isinstance(right, Capsule):
        return polygon_capsule_overlap(left, right)
    if isinstance(left, Capsule) and isinstance(right, Polygon):
        return polygon_capsule_overlap(right, left)
    return capsule_capsule_overlap(left, right)


def _shape_overlap(
    left: list[Circle | Capsule | Polygon],
    right: list[Circle | Capsule | Polygon],
) -> bool:
    for left_primitive in left:
        for right_primitive in right:
            if _primitives_overlap(left_primitive, right_primitive):
                return True
    return False


def _creatures_overlap(left: Creature, right: Creature, fallback_distance: float) -> bool:
    if left.radius <= 0.0 or right.radius <= 0.0:
        return _within_distance(left, right, fallback_distance)
    return _shape_overlap(_creature_primitives(left), _creature_primitives(right))


def _obstacles_overlap(left: Obstacle, right: Obstacle) -> bool:
    return _shape_overlap(_obstacle_primitives(left), _obstacle_primitives(right))


def _creature_overlaps_obstacle(creature: Creature, obstacle: Obstacle) -> bool:
    return _shape_overlap(_creature_primitives(creature), _obstacle_primitives(obstacle))


def _creature_support_distance(creature: Creature, normal_x: float, normal_y: float) -> float:
    relative_primitives = _creature_primitives_at_origin(creature.kind, creature.radius)
    return max(
        primitive_support_distance(normal_x, normal_y, primitive)
        for primitive in relative_primitives
    )


def _obstacle_normal(obstacle: Obstacle, point: Position) -> tuple[float, float]:
    primitive = _obstacle_primitives(obstacle)[0]
    if isinstance(primitive, Circle):
        return normalize(point.x - primitive.center.x, point.y - primitive.center.y)

    closest = polygon_closest_point(point, primitive)
    return normalize(point.x - closest.x, point.y - closest.y)


def _spawn_creature(
    rng: random.Random,
    board: Board,
    creature_id: int,
    creature_speed: float,
    creature_radius: float,
    creature_mass: float,
    obstacles: list[Obstacle],
) -> Creature:
    kind = rng.choice([CreatureType.ROCK, CreatureType.PAPER, CreatureType.SCISSORS])

    min_x = creature_radius
    max_x = board.width - creature_radius
    min_y = creature_radius
    max_y = board.height - creature_radius

    if min_x > max_x or min_y > max_y:
        pos = Position(board.width / 2.0, board.height / 2.0)
    else:
        pos = Position(rng.uniform(min_x, max_x), rng.uniform(min_y, max_y))
        for _ in range(99):
            blocked = False
            candidate = Creature(
                id=creature_id,
                kind=kind,
                pos=pos,
                radius=creature_radius,
                mass=creature_mass,
            )
            for obstacle in obstacles:
                if _creature_overlaps_obstacle(candidate, obstacle):
                    blocked = True
                    break
            if not blocked:
                break
            pos = Position(rng.uniform(min_x, max_x), rng.uniform(min_y, max_y))

    angle = rng.uniform(0.0, math.tau)
    vx = math.cos(angle) * creature_speed
    vy = math.sin(angle) * creature_speed
    return Creature(
        id=creature_id,
        kind=kind,
        pos=pos,
        vx=vx,
        vy=vy,
        radius=creature_radius,
        mass=creature_mass,
    )


def _spawn_obstacles(
    rng: random.Random,
    board: Board,
    obstacle_count: int,
    obstacle_avg_size: float,
) -> list[Obstacle]:
    if obstacle_count <= 0 or obstacle_avg_size <= 0:
        return []

    obstacles: list[Obstacle] = []
    for _ in range(obstacle_count):
        for _attempt in range(50):
            size = rng.uniform(obstacle_avg_size * 0.6, obstacle_avg_size * 1.4)
            min_x = size
            max_x = board.width - size
            min_y = size
            max_y = board.height - size
            if min_x > max_x or min_y > max_y:
                break

            pos = Position(
                rng.uniform(min_x, max_x),
                rng.uniform(min_y, max_y),
            )
            candidate = Obstacle(
                kind=rng.choice(["circle", "square", "triangle"]),
                pos=pos,
                size=size,
                rotation=rng.uniform(0.0, math.tau),
                color=rng.choice(
                    [
                        (120, 125, 135),
                        (165, 109, 86),
                        (98, 140, 110),
                        (143, 112, 168),
                        (184, 146, 79),
                    ]
                ),
            )
            if any(_obstacles_overlap(candidate, other) for other in obstacles):
                continue
            obstacles.append(candidate)
            break
    return obstacles


def create_game(config: SimConfig) -> GameState:
    rng = random.Random(config.random_seed)
    board = Board(width=config.window_width, height=config.window_height)
    obstacles = _spawn_obstacles(
        rng,
        board,
        obstacle_count=config.obstacle_count,
        obstacle_avg_size=config.obstacle_avg_size,
    )
    creatures = [
        _spawn_creature(
            rng,
            board,
            i,
            config.creature_speed,
            config.creature_radius,
            config.creature_mass,
            obstacles,
        )
        for i in range(config.creature_count)
    ]
    creatures = randomize_creature_speeds(
        creatures=creatures,
        rng=rng,
        min_speed=config.creature_speed * config.min_speed_multiplier,
        max_speed=config.creature_speed * config.max_speed_multiplier,
    )
    return GameState(board=board, creatures=creatures, obstacles=obstacles)


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
            radius=creature.radius,
            mass=creature.mass,
        )
        updated_creatures.append(new_creature)
    return updated_creatures


def _grow_creature(creature: Creature, loser_mass: float) -> Creature:
    return Creature(
        id=creature.id,
        kind=creature.kind,
        pos=creature.pos,
        vx=creature.vx,
        vy=creature.vy,
        radius=creature.radius + loser_mass,
        mass=creature.mass + loser_mass,
    )


def _bounce_off_obstacles(creature: Creature, obstacles: list[Obstacle]) -> Creature:
    next_creature = creature

    for obstacle in obstacles:
        if not _creature_overlaps_obstacle(next_creature, obstacle):
            continue

        normal_x, normal_y = _obstacle_normal(obstacle, next_creature.pos)
        extent = _creature_support_distance(next_creature, normal_x, normal_y)
        obstacle_primitive = _obstacle_primitives(obstacle)[0]
        if isinstance(obstacle_primitive, Circle):
            surface_x = obstacle_primitive.center.x + (normal_x * obstacle_primitive.radius)
            surface_y = obstacle_primitive.center.y + (normal_y * obstacle_primitive.radius)
        else:
            closest = polygon_closest_point(next_creature.pos, obstacle_primitive)
            surface_x = closest.x
            surface_y = closest.y

        clamped_x = surface_x + (normal_x * extent)
        clamped_y = surface_y + (normal_y * extent)
        next_vx, next_vy = mirror_vector(
            normal_x,
            normal_y,
            next_creature.vx,
            next_creature.vy,
        )
        next_vx = -next_vx
        next_vy = -next_vy
        next_creature = Creature(
            id=next_creature.id,
            kind=next_creature.kind,
            pos=Position(clamped_x, clamped_y),
            vx=next_vx,
            vy=next_vy,
            radius=next_creature.radius,
            mass=next_creature.mass,
        )

    return next_creature


def _move_creature(
    creature: Creature,
    board: Board,
    obstacles: list[Obstacle],
    default_radius: float | None,
    dt_seconds: float,
) -> Creature:
    radius = (
        creature.radius
        if creature.radius > 0.0
        else (default_radius if default_radius is not None else 0.0)
    )
    next_x = creature.pos.x + (creature.vx * dt_seconds)
    next_y = creature.pos.y + (creature.vy * dt_seconds)
    next_vx = creature.vx
    next_vy = creature.vy

    extent_right = _creature_support_distance(
        Creature(id=creature.id, kind=creature.kind, pos=creature.pos, radius=radius),
        1.0,
        0.0,
    )
    extent_left = _creature_support_distance(
        Creature(id=creature.id, kind=creature.kind, pos=creature.pos, radius=radius),
        -1.0,
        0.0,
    )
    extent_down = _creature_support_distance(
        Creature(id=creature.id, kind=creature.kind, pos=creature.pos, radius=radius),
        0.0,
        1.0,
    )
    extent_up = _creature_support_distance(
        Creature(id=creature.id, kind=creature.kind, pos=creature.pos, radius=radius),
        0.0,
        -1.0,
    )

    if next_x < extent_left or next_x > board.width - extent_right:
        next_vx = -next_vx
        next_x = max(extent_left, min(board.width - extent_right, next_x))

    if next_y < extent_up or next_y > board.height - extent_down:
        next_vy = -next_vy
        next_y = max(extent_up, min(board.height - extent_down, next_y))

    moved_creature = Creature(
        id=creature.id,
        kind=creature.kind,
        pos=Position(next_x, next_y),
        vx=next_vx,
        vy=next_vy,
        radius=radius,
        mass=creature.mass,
    )
    return _bounce_off_obstacles(moved_creature, obstacles)


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
    if mx == 0.0 and my == 0.0:
        mx = left_creature.vx - right_creature.vx
        my = left_creature.vy - right_creature.vy
        if mx == 0.0 and my == 0.0:
            mx = 1.0
    new_vleft = mirror_vector(mx, my, left_creature.vx, left_creature.vy)
    new_vright = mirror_vector(mx, my, right_creature.vx, right_creature.vy)
    new_vleft = -new_vleft[0], -new_vleft[1]
    new_vright = -new_vright[0], -new_vright[1]
    total_mass = max(0.000001, left_creature.mass + right_creature.mass)
    left_factor = min(1.0, (2.0 * right_creature.mass) / total_mass)
    right_factor = min(1.0, (2.0 * left_creature.mass) / total_mass)
    blended_left = (
        left_creature.vx + ((new_vleft[0] - left_creature.vx) * left_factor),
        left_creature.vy + ((new_vleft[1] - left_creature.vy) * left_factor),
    )
    blended_right = (
        right_creature.vx + ((new_vright[0] - right_creature.vx) * right_factor),
        right_creature.vy + ((new_vright[1] - right_creature.vy) * right_factor),
    )
    return blended_left, blended_right
    # TODO(Jonah): implement collision bounce math here.
    #return (left_creature.vx, left_creature.vy), (right_creature.vx, right_creature.vy)
    #return (-left_creature.vx, -left_creature.vy), (-right_creature.vx, -right_creature.vy)
    #return (-right_creature.vx, -right_creature.vy), (-left_creature.vx, -left_creature.vy)
    #return (right_creature.vx, right_creature.vy), (left_creature.vx, left_creature.vy)


def step_game(
    state: GameState,
    rng: random.Random,
    convert_loser_to_winner: bool = True,
    bounce_off_creatures: bool = True,
    creature_radius: float | None = None,
    grow_on_win: bool = False,
    encounter_distance: float = 16.0,
    dt_seconds: float = 1.0,
) -> GameState:
    del rng  # Kept in signature so the app can still pass one RNG object.
    moved_creatures: list[Creature] = []

    for creature in state.creatures:
        moved_creatures.append(
            _move_creature(
                creature,
                state.board,
                state.obstacles,
                creature_radius,
                dt_seconds,
            )
        )

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
                if not _creatures_overlap(left, right, encounter_distance):
                    continue

                pair = _pair_key(left_id, right_id)
                if bounce_off_creatures:
                    collisions_this_tick.add(pair)
                if bounce_off_creatures and pair not in state.active_collision_pairs:
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
                        radius=left.radius,
                        mass=left.mass,
                    )
                    by_id[right_id] = Creature(
                        id=right.id,
                        kind=right.kind,
                        pos=right.pos,
                        vx=next_right_vx,
                        vy=next_right_vy,
                        radius=right.radius,
                        mass=right.mass,
                    )

                winner = rps_winner(left.kind, right.kind)
                if winner is None:
                    continue
                if winner == left.kind:
                    if grow_on_win:
                        by_id[left_id] = _grow_creature(by_id[left_id], by_id[right_id].mass)
                    alive_ids.discard(right_id)
                else:
                    if grow_on_win:
                        by_id[right_id] = _grow_creature(by_id[right_id], by_id[left_id].mass)
                    alive_ids.discard(left_id)
                    break

        return GameState(
            board=state.board,
            creatures=sorted(
                [by_id[c.id] for c in moved_creatures if c.id in alive_ids],
                key=lambda c: c.id,
            ),
            obstacles=state.obstacles,
            tick=state.tick + 1,
            active_collision_pairs=collisions_this_tick,
        )

    collisions_this_tick: set[tuple[int, int]] = set()
    kinds_by_id: dict[int, CreatureType] = {c.id: c.kind for c in moved_creatures}

    for left_index, left_id in enumerate(creature_ids):
        for right_id in creature_ids[left_index + 1 :]:
            left = by_id[left_id]
            right = by_id[right_id]
            if not _creatures_overlap(left, right, encounter_distance):
                continue

            pair = _pair_key(left_id, right_id)
            if bounce_off_creatures:
                collisions_this_tick.add(pair)
            if bounce_off_creatures and pair not in state.active_collision_pairs:
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
                    radius=left.radius,
                    mass=left.mass,
                )
                by_id[right_id] = Creature(
                    id=right.id,
                    kind=right.kind,
                    pos=right.pos,
                    vx=next_right_vx,
                    vy=next_right_vy,
                    radius=right.radius,
                    mass=right.mass,
                )

            left_kind = kinds_by_id[left_id]
            right_kind = kinds_by_id[right_id]
            winner = rps_winner(left_kind, right_kind)
            if winner is None:
                continue

            if winner == left_kind:
                kinds_by_id[right_id] = left_kind
                if grow_on_win:
                    by_id[left_id] = _grow_creature(by_id[left_id], by_id[right_id].mass)
            else:
                kinds_by_id[left_id] = right_kind
                if grow_on_win:
                    by_id[right_id] = _grow_creature(by_id[right_id], by_id[left_id].mass)

    resolved = [
        Creature(
            id=creature.id,
            kind=kinds_by_id[creature.id],
            pos=by_id[creature.id].pos,
            vx=by_id[creature.id].vx,
            vy=by_id[creature.id].vy,
            radius=by_id[creature.id].radius,
            mass=by_id[creature.id].mass,
        )
        for creature in moved_creatures
    ]

    return GameState(
        board=state.board,
        creatures=sorted(resolved, key=lambda c: c.id),
        obstacles=state.obstacles,
        tick=state.tick + 1,
        active_collision_pairs=collisions_this_tick,
    )


def creature_counts(state: GameState) -> Counter[CreatureType]:
    return Counter(c.kind for c in state.creatures)
