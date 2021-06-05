async function postData(url='', data={}) {
    const response = await fetch(url, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    if (!response.ok) {
      throw Error(response.statusText);
    }
    return response.json();
}

class ApiClient {
    constructor() {
        this.baseurl = '../api';
    }

    errHandler(err) {
        alert("An error occurred. Please refresh the page and try again.");
        console.error(err);
    }

    /**
     *
     * @param {func} cb Callback function that takes
     * an array of game objects as an argument.
     * `cb` may be called multiple times if there are
     * more games than can fit in a single API response.
     * @param {string|null} uri Target uri for the API call.
     * Calling members should not use this parameter.
     */
    getGameList(cb, uri=null) {
        const target = uri || `${this.baseurl}/games/`;

        fetch(target)
            .then(res => res.json())
            .then(json => {
                cb(json.results);
                if (json.next) {
                    this.getGameList(cb, json.next);
                }
            })
            .catch(this.errHandler);

    }

    /**
     *
     * @param {number} num_rows
     * @param {number} num_cols
     * @param {number} num_mines
     * @param {func} cb Callback function to handle the result of
     * the create operation. Takes a single argument containing the
     * JSON response from the server.
     */
    createNewGame(num_rows, num_cols, num_mines, cb) {
        if (isNaN(num_rows) || isNaN(num_cols) || isNaN(num_mines)) {
            alert("Invalid number of rows, columns, or mines (NaN).");
            return;
        }
        if (num_rows < 6 || num_rows > 20 || num_cols < 6 || num_cols > 20) {
            alert("Invalid number of rows or columns. Rows and columns must be integers between 6 and 20");
            return;
        }

        const body = {num_rows, num_cols, num_mines}
        postData(`${this.baseurl}/games/`, body)
            .then(cb)
            .catch(this.errHandler);
    }

    getInitialGameState(gameId, cb) {
        fetch(`${this.baseurl}/games/${gameId}/`)
            .then(res => res.json())
            .then(res => {
                const g = new Game(res.tiles, GAME_STATUS_RUNNING);
                cb(g);
            })
            .catch(this.errHandler);
    }

    getGameStateAfterMove(moveId, cb) {
        fetch(`${this.baseurl}/moves/${moveId}`)
            .then(res => res.json())
            .then(res => {
                const g = new Game(res.state.tiles, res.state.status);
                cb(g);
            })
            .catch(this.errHandler);
    }

    /**
     * Retrieves the latest game state using the following
     * procedure:
     * 1. Try getting the move history for `gameId`.
     * If there are moves, then it gets the game state
     * after applying the latest move.
     * 2. If there are no moves, tries to get the initial
     * game state.
     * 3. If that fails, the gameId does not exist.
     *
     * @param {number} gameId
     * @param {func} cb
     */
    getLatestGameState(gameId, cb) {

        fetch(`${this.baseurl}/moves/?game_id=${gameId}`)
            .then(res => res.json())
            .then(res => {
                if (res.results) {
                    // the API should return moves in order,
                    // but it doesn't hurt to make sure
                    // we get the latest one
                    let latest = res.results[0];
                    for (let mv of res.results) {
                        if (mv.order > latest.order) {
                            latest = mv;
                        }
                    }

                    this.getGameStateAfterMove(latest.id, cb);


                } else {
                    // no moves for this game exist.
                    // Try fetching the initial game state
                    this.getInitialGameState(gameId, cb);
                }
            })
            .catch(this.errHandler);
    }
}