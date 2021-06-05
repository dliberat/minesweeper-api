# minesweeper-API
API test

# Getting Started

**To launch the development server**

1. Ensure Docker and Docker Compose are installed (https://docs.docker.com/compose/install/)
2. cd into the project directory and run `docker-compose up`
3. Browse to [http://localhost:8000/api/](http://localhost:8000/api/) to view the browsable API.
4. Browse to [http://localhost:8000/static/client.html](http://localhost:8000/static/client.html) to play the game.

# How to play

## Starting a new game

Start a new game by making a `POST` request to `/api/games/`.
The POST body must contain the following fields:

|Field       | Data Type | Description |
|------------|-----------|-------------|
|`num_rows`  | Integer   | Number of rows for the game. Between 6 and 20. |
|`num_cols`  | Integer   | Number of columns for the game. Between 6 and 20. |
|`num_mines` | Integer   | Number of mines for the game. Between 2 and `num_rows x num_cols` |

**Example request**

```json
{
    "num_rows": 10,
    "num_cols": 10,
    "num_mines": 40
}
```

**Example response**

```json
{
    "id": 14,
    "num_rows": 10,
    "num_cols": 10,
    "num_mines": 40,
    "created_at": "2021-06-05T05:04:22.273316Z"
}
```

## Viewing the initial state of a game

Once a new game has been created, you can view its initial state (before any moves have been made) by sending a `GET` request to `/api/games/<game id>`.
The initial game state is returned in the `tiles` field.

**Example response (array contents trimmed)**
```json
{
    "id": 14,
    "num_rows": 10,
    "num_cols": 10,
    "num_mines": 40,
    "created_at": "2021-06-05T05:04:22.273316Z",
    "tiles": [
        [...],
        [...],
        [...],
        ...
    ]
}
```

## Making a move

Apply a new move to a game by sending a `POST` request to the `/api/moves/` endpoint.

The `POST` body should contain the following fields:

| Field    | Data Type | Description   |
|----------|-----------|---------------|
|`game_id` | Integer   | Unique identifier for the game to modify |
|`row`     | Integer   | Row index of the tile that was clicked.  |
|`col`     | Integer   | Column index of the tile that was clicked. |
|`action`  | String    | One of "R" (reveal) or "F" (flag). Applying an "F" move to an already flagged tile will cause that flag to be removed. Applying any move to an already revealed tile will fail.|

**Example request (reveal the top left corner of the board)**

```json
{
    "game_id": 14,
    "row": 0,
    "col": 0,
    "action": "R"
}
```

The 201 response when a new move is created includes the state of the game after that move has been applied.

## Viewing the game's move history

A complete list of the moves made in a game can be viewed by sending a `GET` request to `/api/moves/` and filtering by the desired game ID.
To filter by game ID, pass the game ID as a URL parameter in the request as follows: `/api/moves/?game_id=14`

## Viewing the game state at a particular point in time

Making a `GET` request to `/api/moves/<move id>/` will return a `state` field that shows the state of the game after that move was applied.

**Example response (array contents trimmed)**

```json
{
    "id": 18,
    "game_id": 14,
    "order": 3,
    "row": 6,
    "col": 0,
    "action": "R",
    "state": {
        "status": 0,
        "tiles": [
            [...],
            [...],
            [...],
            ...
        ]
    }
```


# ADR

## Persistence layer: Sqlite or Postgres?

- Opting for most familiar tech due to time constraints
- Sqlite is lightweight, but Postgres has ArrayField which is a natural fit for game board
- Result: Use Postgres

## Front/Back deployment strategy

- Separating the front-end into its own app would probably be ideal
- However, for the purposes of this demo, a barebones front-end with only a few static files should suffice
- Decoupled design means that front end can be easily refactored into separate app if necessary
- Result: Develop front-end in the same repo and serve as static content.

## When revealing adjacent cells recursively, do flags break recursion?

- Decision: No.
- Rationale: Even if the flag breaks the recursion, it would become instantly apparent that the flag was not needed on that tile.

## Object model strategy for storing moves

- Best to store a complete move history. It's not strictly speaking necessary based on the project requirements, but usually a good idea for implementing undos, replays, etc.
- Is it necessary to store each intermediate state of the game, or is it sufficient to store only the moves and re-create the game state on the fly each time?
- Result: Recreating the game state on the fly is fast, and easier to implement. If performance requirements are stricter in the future, this decision can be easily revised.

## Limits on game size

- UI design can get complicated with arbitrarily large game sizes (eg. 1,000,000 x 1,000,000 !?)
- Tricky edge cases can occur with extremely small game sizes (eg., 0x0, 1x1)
- Result: Set arbitrary "sane" limits on game size (minimum 6x6, maximum 20x20)
- Result: Set arbitrary "sane" limit on mine count (minimum=2, maximum=total number of grid squares)

## Game tile representation

- Each tile needs to have information about whether it has been revealed or not, whether it has been flagged or not, and whether it contains a mine or not.
- The revealed/not revealed/flag states are mutually exclusive, so they could all be represented with a single three-state variable, but is mine/is not mine would need to be stored separately.
- In addition, if the tile does not maintain information about its neighboring mine count, we would need to iterate over its neighbors whenever we need that information (this might not be so bad, actually. Maybe this only happens when revealing a tile?)
- All of this state could be stored either in multiple 2D arrays, or in a single array whose values contain all of the required state.
- Having neighboring mine counts directly accessible as part of the tile value is convenient so it's preferrable to save that as part of the tile object.
- Operations and data storage are efficient if we represent the tiles as integers.
- Result: Store tile data as integers. Use different bits to track the different kinds of state.
- Drawback: Visually interpreting an array of tiles is not practical.
