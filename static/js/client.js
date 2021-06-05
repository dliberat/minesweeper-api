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
            });

    }
}