const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const express = require('express');
const multer = require('multer');

const { APP_PORT, GAME_ORIGIN } = require('./config');
const { readDb, writeDb } = require('./db');
const { validateAndExtractZip, ZipValidationError } = require('./validateZip');

const GAMES_DIR = path.join(__dirname, '..', 'games');
const PUBLIC_DIR = path.join(__dirname, '..', 'public');

const MAX_UPLOAD_BYTES = 60 * 1024 * 1024; // buffer acima do limite de 50MB pós-extração
const MAX_TITLE_LEN = 80;
const MAX_DESCRIPTION_LEN = 500;
const MAX_REPORT_REASON_LEN = 500;

const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '10kb' }));

// CSP do site principal: só carrega o próprio JS/CSS (sem inline), pra
// reduzir risco de XSS nas nossas próprias páginas. Isto é separado — e
// bem mais permissivo em relação a rede — da CSP aplicada aos jogos em si
// no game-server.
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "script-src 'self'",
      "style-src 'self'",
      "img-src 'self' data:",
      `frame-src ${GAME_ORIGIN}`,
      "object-src 'none'",
      "base-uri 'none'",
    ].join('; ')
  );
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  next();
});

app.use(express.static(PUBLIC_DIR));

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: MAX_UPLOAD_BYTES, files: 1 },
  fileFilter: (req, file, cb) => {
    const isZipName = /\.zip$/i.test(file.originalname);
    const isZipMime = [
      'application/zip',
      'application/x-zip-compressed',
      'application/octet-stream',
    ].includes(file.mimetype);
    if (!isZipName || !isZipMime) {
      return cb(new Error('Envie um arquivo .zip válido.'));
    }
    cb(null, true);
  },
});

function isNonEmptyString(v) {
  return typeof v === 'string' && v.trim().length > 0;
}

app.post('/api/upload', (req, res) => {
  upload.single('zip')(req, res, (err) => {
    if (err) {
      return res.status(400).json({ error: err.message });
    }
    if (!req.file) {
      return res.status(400).json({ error: 'Nenhum arquivo enviado.' });
    }

    const title = (req.body.title || '').trim().slice(0, MAX_TITLE_LEN);
    const description = (req.body.description || '').trim().slice(0, MAX_DESCRIPTION_LEN);

    if (!isNonEmptyString(title)) {
      return res.status(400).json({ error: 'Título é obrigatório.' });
    }

    const gameId = crypto.randomUUID();
    const destDir = path.join(GAMES_DIR, gameId);

    try {
      validateAndExtractZip(req.file.buffer, destDir);
    } catch (e) {
      // Limpa qualquer coisa parcialmente extraída antes da falha.
      fs.rmSync(destDir, { recursive: true, force: true });
      if (e instanceof ZipValidationError) {
        return res.status(400).json({ error: e.message });
      }
      console.error(e);
      return res.status(500).json({ error: 'Falha ao processar o zip.' });
    }

    const db = readDb();
    db.games.push({
      id: gameId,
      title,
      description,
      createdAt: new Date().toISOString(),
      status: 'published',
    });
    writeDb(db);

    res.status(201).json({ id: gameId });
  });
});

app.get('/api/games', (req, res) => {
  const db = readDb();
  const games = db.games
    .filter((g) => g.status === 'published')
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .map(({ id, title, description, createdAt }) => ({ id, title, description, createdAt }));
  res.json(games);
});

app.get('/game/:id', (req, res) => {
  const { id } = req.params;
  if (!/^[a-f0-9-]{36}$/.test(id)) {
    return res.status(400).send('ID de jogo inválido.');
  }
  const db = readDb();
  const game = db.games.find((g) => g.id === id && g.status === 'published');
  if (!game) {
    return res.status(404).send('Jogo não encontrado.');
  }

  const escapedTitle = game.title.replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));

  res.send(`<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapedTitle}</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="topbar">
  <a href="/" class="brand">&larr; Voltar</a>
  <h1>${escapedTitle}</h1>
  <button id="report-btn" class="btn btn-ghost">Denunciar</button>
</header>
<main class="game-frame-wrap">
  <iframe
    src="${GAME_ORIGIN}/g/${id}/index.html"
    sandbox="allow-scripts allow-pointer-lock"
    referrerpolicy="no-referrer"
    class="game-frame"
    title="${escapedTitle}"
  ></iframe>
</main>
<dialog id="report-dialog">
  <form id="report-form" method="dialog">
    <p>Por que você está denunciando este jogo?</p>
    <textarea id="report-reason" maxlength="${MAX_REPORT_REASON_LEN}" required></textarea>
    <div class="dialog-actions">
      <button type="button" id="report-cancel" class="btn btn-ghost">Cancelar</button>
      <button type="submit" class="btn">Enviar denúncia</button>
    </div>
  </form>
</dialog>
<script src="/game.js" data-game-id="${id}"></script>
</body>
</html>`);
});

app.post('/api/games/:id/report', (req, res) => {
  const { id } = req.params;
  if (!/^[a-f0-9-]{36}$/.test(id)) {
    return res.status(400).json({ error: 'ID inválido.' });
  }
  const db = readDb();
  const game = db.games.find((g) => g.id === id);
  if (!game) {
    return res.status(404).json({ error: 'Jogo não encontrado.' });
  }
  const reason = (req.body.reason || '').trim().slice(0, MAX_REPORT_REASON_LEN);
  if (!isNonEmptyString(reason)) {
    return res.status(400).json({ error: 'Motivo é obrigatório.' });
  }
  db.reports.push({
    id: crypto.randomUUID(),
    gameId: id,
    reason,
    createdAt: new Date().toISOString(),
  });
  writeDb(db);
  res.status(201).json({ ok: true });
});

// --- Rotas administrativas -------------------------------------------------
// ATENÇÃO: este MVP não tem autenticação nestas rotas. Antes de qualquer
// deploy real, isto precisa ficar atrás de login de admin (sessão, token,
// o que for) — ver README, seção "Limitações conhecidas".

app.get('/api/admin/games', (req, res) => {
  const db = readDb();
  const reportCounts = db.reports.reduce((acc, r) => {
    acc[r.gameId] = (acc[r.gameId] || 0) + 1;
    return acc;
  }, {});
  const games = db.games.map((g) => ({
    ...g,
    reportCount: reportCounts[g.id] || 0,
  }));
  res.json(games);
});

app.delete('/api/games/:id', (req, res) => {
  const { id } = req.params;
  if (!/^[a-f0-9-]{36}$/.test(id)) {
    return res.status(400).json({ error: 'ID inválido.' });
  }
  const db = readDb();
  const before = db.games.length;
  db.games = db.games.filter((g) => g.id !== id);
  db.reports = db.reports.filter((r) => r.gameId !== id);
  writeDb(db);
  fs.rmSync(path.join(GAMES_DIR, id), { recursive: true, force: true });
  if (db.games.length === before) {
    return res.status(404).json({ error: 'Jogo não encontrado.' });
  }
  res.json({ ok: true });
});

app.listen(APP_PORT, () => {
  console.log(`[app-server] site principal em http://localhost:${APP_PORT}`);
});
