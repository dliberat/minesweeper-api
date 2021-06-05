
function populateGameList() {
    const dash = $('#games-list');
    dash.empty();

    const client = new ApiClient();

    client.getGameList(gameList => {
        for (let game of gameList) {
            const li = $(`<li id="game--link--${game.id}"></li>`);
            li.text(`Game #${game.id} (${game.num_rows} x ${game.num_cols})`);
            dash.append(li);
        }
    });
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

function handleNewGameResponse(response) {
    populateGameList();
}

document.addEventListener('DOMContentLoaded', populateGameList);
$('#input--submit').on('click', handleNewGameBtnClicked);