# minesweeper-API
API test

# Getting Started

**To launch the development server**

1. Ensure Docker and Docker Compose are installed (https://docs.docker.com/compose/install/)
2. cd into the project directory and run `docker-compose up`
3. Browse to [http://localhost:8000/api/](http://localhost:8000/api/) to view the browsable API.
4. Browse to [http://localhost:8000/static/client.html](http://localhost:8000/static/client.html) to play the game.

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
