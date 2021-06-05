class Game {

    static STATUS_RUNNING = 0;
    static STATUS_WON = 1;
    static STATUS_LOST = 2;

    constructor(gameId, tileArray, status) {
        this.gameId = gameId;
        this.status = status;

        // convert array of integers to Tile objects
        this.tiles = []
        for (let i = 0; i < tileArray.length; i++) {
            this.tiles.push([])
            for (let j = 0; j < tileArray[i].length; j++) {
                this.tiles[i].push(new Tile(tileArray[i][j], this));
            }
        }

    }

    statusAsText() {
        if (this.status === Game.STATUS_RUNNING) {
            return 'Playing';
        }
        if (this.status === Game.STATUS_WON) {
            return 'You won!';
        }
        if (this.status === Game.STATUS_LOST) {
            return 'You lost!';
        }
        console.error('Invalid game status');
    }

    minesRemaining() {
        let ttl = 0;
        for (let row of this.tiles) {
            for (let t of row) {
                if (t.isMine()) {
                    ttl += 1;
                }
                if (t.isFlag()) {
                    ttl -= 1;
                }
            }
        }

        if (ttl < 0) {
            ttl = 0;
        }
        return ttl;
    }

    renderGrid(target_element) {
        target_element.empty()

        for (let i = 0; i < this.tiles.length; i++) {
            const tr = $('<tr>');
            for (let j = 0; j < this.tiles[i].length; j++) {
                const tile = this.tiles[i][j]
                tr.append(tile.render(i, j));
            }
            target_element.append(tr)
        }
    }

}