const rowsEl = document.getElementById('admin-rows');

async function loadGames() {
  const res = await fetch('/api/admin/games');
  const games = await res.json();
  rowsEl.textContent = '';

  for (const game of games) {
    const tr = document.createElement('tr');

    const titleTd = document.createElement('td');
    titleTd.textContent = game.title;

    const dateTd = document.createElement('td');
    dateTd.textContent = new Date(game.createdAt).toLocaleString('pt-BR');

    const reportsTd = document.createElement('td');
    reportsTd.textContent = String(game.reportCount);
    if (game.reportCount > 0) reportsTd.className = 'tag-warn';

    const actionsTd = document.createElement('td');
    const delBtn = document.createElement('button');
    delBtn.className = 'btn btn-danger';
    delBtn.textContent = 'Remover';
    delBtn.addEventListener('click', () => removeGame(game.id));
    actionsTd.appendChild(delBtn);

    tr.append(titleTd, dateTd, reportsTd, actionsTd);
    rowsEl.appendChild(tr);
  }
}

async function removeGame(id) {
  if (!confirm('Remover este jogo definitivamente?')) return;
  await fetch(`/api/games/${encodeURIComponent(id)}`, { method: 'DELETE' });
  loadGames();
}

loadGames();
