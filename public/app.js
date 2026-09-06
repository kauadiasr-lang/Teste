async function loadGames() {
  const grid = document.getElementById('games-grid');
  const emptyState = document.getElementById('empty-state');

  let games = [];
  try {
    const res = await fetch('/api/games');
    games = await res.json();
  } catch {
    grid.textContent = 'Não foi possível carregar os jogos.';
    return;
  }

  if (games.length === 0) {
    emptyState.hidden = false;
    return;
  }

  for (const game of games) {
    const card = document.createElement('a');
    card.className = 'game-card';
    card.href = `/game/${encodeURIComponent(game.id)}`;

    const title = document.createElement('h3');
    title.textContent = game.title; // textContent evita XSS armazenado

    const desc = document.createElement('p');
    desc.textContent = game.description || '';

    card.append(title, desc);
    grid.appendChild(card);
  }
}

loadGames();
