from dataclasses import dataclass
import math

from .board import Position


@dataclass(frozen=True)
class Circle:
    center: Position
    radius: float


@dataclass(frozen=True)
class Capsule:
    start: Position
    end: Position
    radius: float


@dataclass(frozen=True)
class Polygon:
    vertices: tuple[Position, ...]


def dot(ax: float, ay: float, bx: float, by: float) -> float:
    return (ax * bx) + (ay * by)


def length_sq(dx: float, dy: float) -> float:
    return (dx * dx) + (dy * dy)


def distance_sq(a: Position, b: Position) -> float:
    return length_sq(a.x - b.x, a.y - b.y)


def closest_point_on_segment(point: Position, start: Position, end: Position) -> Position:
    seg_x = end.x - start.x
    seg_y = end.y - start.y
    seg_len_sq = length_sq(seg_x, seg_y)
    if seg_len_sq == 0.0:
        return start

    t = dot(point.x - start.x, point.y - start.y, seg_x, seg_y) / seg_len_sq
    t = max(0.0, min(1.0, t))
    return Position(start.x + (seg_x * t), start.y + (seg_y * t))


def distance_sq_point_segment(point: Position, start: Position, end: Position) -> float:
    closest = closest_point_on_segment(point, start, end)
    return distance_sq(point, closest)


def _orientation(a: Position, b: Position, c: Position) -> float:
    return ((b.x - a.x) * (c.y - a.y)) - ((b.y - a.y) * (c.x - a.x))


def _on_segment(a: Position, b: Position, c: Position) -> bool:
    return (
        min(a.x, c.x) <= b.x <= max(a.x, c.x)
        and min(a.y, c.y) <= b.y <= max(a.y, c.y)
    )


def segments_intersect(a1: Position, a2: Position, b1: Position, b2: Position) -> bool:
    o1 = _orientation(a1, a2, b1)
    o2 = _orientation(a1, a2, b2)
    o3 = _orientation(b1, b2, a1)
    o4 = _orientation(b1, b2, a2)

    if (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0):
        return True

    if o1 == 0 and _on_segment(a1, b1, a2):
        return True
    if o2 == 0 and _on_segment(a1, b2, a2):
        return True
    if o3 == 0 and _on_segment(b1, a1, b2):
        return True
    if o4 == 0 and _on_segment(b1, a2, b2):
        return True
    return False


def point_in_polygon(point: Position, polygon: Polygon) -> bool:
    inside = False
    vertices = polygon.vertices
    for index, left in enumerate(vertices):
        right = vertices[(index + 1) % len(vertices)]
        intersects = ((left.y > point.y) != (right.y > point.y)) and (
            point.x
            < ((right.x - left.x) * (point.y - left.y) / (right.y - left.y)) + left.x
        )
        if intersects:
            inside = not inside
    return inside


def circle_circle_overlap(left: Circle, right: Circle) -> bool:
    radius_sum = left.radius + right.radius
    return distance_sq(left.center, right.center) <= radius_sum * radius_sum


def circle_polygon_overlap(circle: Circle, polygon: Polygon) -> bool:
    if point_in_polygon(circle.center, polygon):
        return True

    vertices = polygon.vertices
    for index, start in enumerate(vertices):
        end = vertices[(index + 1) % len(vertices)]
        if distance_sq_point_segment(circle.center, start, end) <= circle.radius * circle.radius:
            return True
    return False


def polygon_polygon_overlap(left: Polygon, right: Polygon) -> bool:
    for index, start in enumerate(left.vertices):
        end = left.vertices[(index + 1) % len(left.vertices)]
        for other_index, other_start in enumerate(right.vertices):
            other_end = right.vertices[(other_index + 1) % len(right.vertices)]
            if segments_intersect(start, end, other_start, other_end):
                return True

    return point_in_polygon(left.vertices[0], right) or point_in_polygon(right.vertices[0], left)


def circle_capsule_overlap(circle: Circle, capsule: Capsule) -> bool:
    radius_sum = circle.radius + capsule.radius
    return (
        distance_sq_point_segment(circle.center, capsule.start, capsule.end)
        <= radius_sum * radius_sum
    )


def capsule_capsule_overlap(left: Capsule, right: Capsule) -> bool:
    radius_sum = left.radius + right.radius
    if segments_intersect(left.start, left.end, right.start, right.end):
        return True

    distances = [
        distance_sq_point_segment(left.start, right.start, right.end),
        distance_sq_point_segment(left.end, right.start, right.end),
        distance_sq_point_segment(right.start, left.start, left.end),
        distance_sq_point_segment(right.end, left.start, left.end),
    ]
    return min(distances) <= radius_sum * radius_sum


def polygon_capsule_overlap(polygon: Polygon, capsule: Capsule) -> bool:
    if point_in_polygon(capsule.start, polygon) or point_in_polygon(capsule.end, polygon):
        return True

    vertices = polygon.vertices
    for index, start in enumerate(vertices):
        end = vertices[(index + 1) % len(vertices)]
        if capsule_capsule_overlap(
            capsule,
            Capsule(start=start, end=end, radius=0.0),
        ):
            return True
    return False


def polygon_closest_point(point: Position, polygon: Polygon) -> Position:
    best_point = polygon.vertices[0]
    best_distance = distance_sq(point, best_point)
    vertices = polygon.vertices
    for index, start in enumerate(vertices):
        end = vertices[(index + 1) % len(vertices)]
        candidate = closest_point_on_segment(point, start, end)
        candidate_distance = distance_sq(point, candidate)
        if candidate_distance < best_distance:
            best_point = candidate
            best_distance = candidate_distance
    return best_point


def primitive_support_distance(normal_x: float, normal_y: float, primitive: Circle | Capsule | Polygon) -> float:
    if isinstance(primitive, Circle):
        return primitive.radius
    if isinstance(primitive, Capsule):
        return max(
            dot(primitive.start.x, primitive.start.y, normal_x, normal_y),
            dot(primitive.end.x, primitive.end.y, normal_x, normal_y),
        ) + primitive.radius
    return max(dot(vertex.x, vertex.y, normal_x, normal_y) for vertex in primitive.vertices)


def normalize(dx: float, dy: float) -> tuple[float, float]:
    magnitude = math.sqrt(length_sq(dx, dy))
    if magnitude == 0.0:
        return 1.0, 0.0
    return dx / magnitude, dy / magnitude
