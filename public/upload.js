const form = document.getElementById('upload-form');
const messageBox = document.getElementById('form-message');

function showMessage(text, type) {
  messageBox.textContent = text;
  messageBox.className = `message ${type}`;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  messageBox.textContent = '';
  messageBox.className = '';

  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;

  try {
    const formData = new FormData(form);
    const res = await fetch('/api/upload', { method: 'POST', body: formData });
    const data = await res.json();

    if (!res.ok) {
      showMessage(data.error || 'Falha ao publicar o jogo.', 'error');
      return;
    }

    showMessage('Jogo publicado! Redirecionando...', 'success');
    setTimeout(() => {
      window.location.href = `/game/${encodeURIComponent(data.id)}`;
    }, 800);
  } catch {
    showMessage('Erro de rede ao enviar o jogo.', 'error');
  } finally {
    submitBtn.disabled = false;
  }
});
