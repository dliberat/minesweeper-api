
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



document.addEventListener('DOMContentLoaded', populateGameList);