
function populateGameList() {
    const dash = $('#games-list');
    dash.empty();

    const client = new ApiClient();

    client.getGameList(gameList => {
        for (let game of gameList) {
            const li = $(`<li id="game--link--${game.id}"></li>`);
            li.text(`Game #${game.id} (${game.num_rows} x ${game.num_cols})`);
            li.on('click', handleGameListClicked);
            dash.append(li);
        }
    });
}

function renderGame(game) {
    const hud = $('#game--header')
    hud.css('display', 'grid');

    const tbody = $('#game--tbody');
    const mRemaining = $('#game--mines-remaining');
    const title = $('#game--title');
    const status = $('#game--status');

    game.renderGrid(tbody);
    mRemaining.text(game.minesRemaining());
    title.text(`Game #${game.gameId}`);
    status.text(game.statusAsText());
}

function handleGameListClicked(e) {
    const gameId = e.target.id.slice(12);

    const client = new ApiClient();
    client.getLatestGameState(gameId, renderGame);
}

function handleNewGameBtnClicked() {

    const inputRows = $("#input--numrows");
    const inputCols = $("#input--numcols");
    const inputMines = $("#input--nummines");
    const rows = parseInt(inputRows.val(), 10);
    const cols = parseInt(inputCols.val(), 10);
    const mines = parseInt(inputMines.val(), 10);

    const client = new ApiClient();
    client.createNewGame(rows, cols, mines, handleNewGameResponse);

}

function handleNewGameResponse(res) {
    populateGameList();
    const client = new ApiClient();
    client.getLatestGameState(res.id, renderGame);
}

function handleTileAction(game, row, col, action, isVisible) {
    if (game.status !== Game.STATUS_RUNNING) {
      // can't click once game is over
      return;
    }
    if (isVisible) {
      // can't click on an already revealed tile
      return;
    }

    const client = new ApiClient();
    client.makeMove(game.gameId, row, col, action, renderGame);
}

function handleContentLoaded() {
    const client = new ApiClient();
    const a = $('#login--link');

    client.isLoggedIn(isLoggedIn => {
        if (!isLoggedIn) {

            a.attr('href', '../api-auth/login/?next=/static/client.html');
            a.text('Log In');

        } else {

            a.attr('href', '../api-auth/logout/?next=/static/client.html');
            a.text('Log Out');

            populateGameList();
            $('#input--submit').on('click', handleNewGameBtnClicked);

        }

    })
}

document.addEventListener('DOMContentLoaded', handleContentLoaded);
