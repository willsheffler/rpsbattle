# Session Log - 2026-02-16

## Session Info
- Participants: Jonah
- Focus: Record baseline state of the project with screenshots

## Note
The 3 most recent screenshots are the beginning, middle, and end of our starting point of the program as it is now.

## Observation 1
At the start there is a mix, but in the middle scissors had the most. In the end rock won because the scissors killed all of the papers, so the rock could not be killed.

### Corresponding Screenshots
![Beginning state](assets/2026-02-16-starting-point/beginning.png)
![Middle state](assets/2026-02-16-starting-point/middle.png)
![End state](assets/2026-02-16-starting-point/end.png)

## Jonah Bounce Function And Diagram
Jonah wrote the bounce mechanic function using mirror reflection and reversal.

```python
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
```

```mermaid
flowchart TD
    A[Collision detected] --> B[Build mirror vector from creature positions]
    B --> C[Reflect left velocity using mirror vector]
    B --> D[Reflect right velocity using mirror vector]
    C --> E[Reverse reflected left velocity]
    D --> F[Reverse reflected right velocity]
    E --> G[Return two new velocity vectors]
    F --> G
```

## Observation 2
Simulations go on a lot longer when the creatures bounce off each other due to the fact that they do not mix as well. The previous behavior allowed creatures to pass through each other, allowing them to mix more effectively. \(Will: in the final screenshot from observation 1 without bouncing, at 2431 ticks the sim was all rock and had been for a while. in the screenshot here, at tick 3751 there is still a good mix\)

### Corresponding Screenshot
![Newest bounce state](assets/2026-02-16-starting-point/newest-bounce.png)

## Source Screenshot Files
- `screenshots/rpsbattle-20260216-133120-881097.png`
- `screenshots/rpsbattle-20260216-133133-893626.png`
- `screenshots/rpsbattle-20260216-133140-237537.png`
- `screenshots/rpsbattle-20260216-143836-435335.png`

## Quiz Log
- Q1: What does `mirror_vector(mx, my, x, y)` return?
  - A1: It mirrors the input vector x, y through the mirror vector mx, my and returns it.
- Q2: In `bounce_velocity`, what are `mx` and `my` built from?
  - A2: mx and my are built from subtracting the right_creature position from the left_creature position.
- Q3: Why do we track `active_collision_pairs` in `GameState`?
  - A3: We track active_collision_pairs to prevent multiple calls to the bounce function during a single collision.
- Q4: If two creatures stay overlapped for 3 ticks, how many times should they bounce?
  - A4: Once.
- Q5: After two creatures separate and collide again later, should they bounce again?
  - A5: Yes, they should.

## Quiz Grade
- Score: 5/5
- Result: Excellent understanding of mirror-vector bounce math and collision-pair tracking behavior.
