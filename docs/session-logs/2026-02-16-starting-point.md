# Session Log - 2026-02-16

## Session Info
- Participants: Jonah
- Focus: Record baseline state of the project with screenshots

## Note
The 3 most recent screenshots are the beginning, middle, and end of our starting point of the program as it is now.

## Observation Note
At the start there is a mix, but in the middle scissors had the most. In the end rock won because the scissors killed all of the papers, so the rock could not be killed.

## Jonah Function Note
The function that Jonah wrote creates a graphic of the bouncing mechanic.

## Bouncing Mechanic Graphic
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

## Evidence
### Beginning
![Beginning state](assets/2026-02-16-starting-point/beginning.png)

### Middle
![Middle state](assets/2026-02-16-starting-point/middle.png)

### End
![End state](assets/2026-02-16-starting-point/end.png)

## Source Screenshot Files
- `screenshots/rpsbattle-20260216-133120-881097.png`
- `screenshots/rpsbattle-20260216-133133-893626.png`
- `screenshots/rpsbattle-20260216-133140-237537.png`
