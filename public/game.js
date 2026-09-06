const gameId = document.currentScript.dataset.gameId;
const dialog = document.getElementById('report-dialog');
const form = document.getElementById('report-form');
const reasonInput = document.getElementById('report-reason');

document.getElementById('report-btn').addEventListener('click', () => {
  reasonInput.value = '';
  dialog.showModal();
});

document.getElementById('report-cancel').addEventListener('click', () => {
  dialog.close();
});

form.addEventListener('submit', async () => {
  const reason = reasonInput.value.trim();
  if (!reason) return;
  try {
    await fetch(`/api/games/${encodeURIComponent(gameId)}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
    });
  } catch {
    // Falha silenciosa: não é crítico bloquear o jogo por causa disso.
  }
});
