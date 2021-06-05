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
}