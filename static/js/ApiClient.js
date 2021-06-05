class ApiClient {
    constructor() {
        this.baseurl = '../api';
    }

    _getCsrf(name='csrftoken') {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async _get(url) {
        const params = {headers: {'X-CSRFToken': this._getCsrf()}}
        const response = await fetch(url, params);
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response.json();
    }

    async _post(url, data={}) {
        const params = {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this._getCsrf(),
            },
            body: JSON.stringify(data),
        }

        const response = await fetch(url, params);
        if (!response.ok) {
          throw Error(response.statusText);
        }
        return response.json();
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

        this._get(target)
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
        if (num_mines < 2 || num_mines >= num_rows*num_cols) {
            alert("Invalid number of mines. Number of mines must be greater than 1 and less than the total number of tiles in the game.");
            return;
        }

        const body = {num_rows, num_cols, num_mines}
        this._post(`${this.baseurl}/games/`, body)
            .then(cb)
            .catch(this.errHandler);
    }

    getInitialGameState(gameId, cb) {
        this._get(`${this.baseurl}/games/${gameId}/`)
            .then(res => {
                const g = new Game(res.id, res.tiles, Game.STATUS_RUNNING);
                cb(g);
            })
            .catch(this.errHandler);
    }

    getGameStateAfterMove(moveId, cb) {
        this._get(`${this.baseurl}/moves/${moveId}/`)
            .then(res => {
                const g = new Game(res.game_id, res.state.tiles, res.state.status);
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

        this._get(`${this.baseurl}/moves/?game_id=${gameId}&ordering=-order`)
            .then(res => {
                if (res.results && res.results.length > 0) {
                    // By sorting by -order, we guarantee
                    // the latest move will be on top
                    let latest = res.results[0];
                    this.getGameStateAfterMove(latest.id, cb);


                } else {
                    // no moves for this game exist.
                    // Try fetching the initial game state
                    this.getInitialGameState(gameId, cb);
                }
            })
            .catch(this.errHandler);
    }

    /**
     *
     * @param {number} gameId
     * @param {number} row
     * @param {number} col
     * @param {string} action 'R' to reveal a tile, or 'F' to flag
     * or unflag a tile.
     * @param {func} cb Callback function called with the updated
     * game state after the move is applied.
     */
    makeMove(gameId, row, col, action, cb) {
        const body = {
            row,
            col,
            action,
            game_id: gameId,
        }

        this._post(`${this.baseurl}/moves/`, body)
            .then(res => {
                const gm = new Game(res.game_id, res.state.tiles, res.state.status);
                cb(gm);
            })
            .catch(this.errHandler);
    }

    /**
     * Somewhat hacky way of determining if the user is logged in.
     */
    isLoggedIn(cb) {

        const params = {headers: {'X-CSRFToken': this._getCsrf()}}
        fetch(`${this.baseurl}/games/`, params)
            .catch(cb(false))
            .then(response => {
                if (response.status === 200) {
                    cb(true);
                } else {
                    cb(false);
                }
            });
    }
}
