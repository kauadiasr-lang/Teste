const path = require('path');
const express = require('express');
const { GAME_PORT, APP_ORIGIN } = require('./config');

const GAMES_DIR = path.join(__dirname, '..', 'games');

const app = express();

// Nunca expor detalhes de stack/framework em erros para conteúdo não confiável.
app.disable('x-powered-by');

app.use((req, res, next) => {
  // CSP do jogo: só pode carregar script/estilo/mídia da própria origem do
  // jogo (bloqueia CDN externo e scripts remotos maliciosos), sem eval,
  // sem rede de saída (connect-src 'none' — sem fetch/XHR/WebSocket; a v2
  // com multiplayer vai liberar isso só pro servidor de relay), sem enviar
  // formulários pra fora, e só pode ser embutido em iframe pelo site
  // principal (frame-ancestors).
  res.setHeader(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data:",
      "font-src 'self' data:",
      "media-src 'self'",
      "connect-src 'none'",
      "object-src 'none'",
      "base-uri 'none'",
      "form-action 'none'",
      `frame-ancestors ${APP_ORIGIN}`,
    ].join('; ')
  );
  res.setHeader('X-Content-Type-Options', 'nosniff');
  // Nunca deixar esta origem guardar credenciais de sessão do site principal.
  res.setHeader('Cache-Control', 'no-store');
  next();
});

app.use(
  '/g/:gameId',
  (req, res, next) => {
    // Bloqueia IDs de jogo fora do formato esperado antes de tocar no disco.
    if (!/^[a-zA-Z0-9-]+$/.test(req.params.gameId)) {
      return res.status(400).send('ID de jogo inválido');
    }
    next();
  },
  (req, res, next) => {
    const gameDir = path.join(GAMES_DIR, req.params.gameId);
    express.static(gameDir, {
      dotfiles: 'deny',
      index: 'index.html',
      redirect: false,
    })(req, res, next);
  }
);

app.use((req, res) => {
  res.status(404).send('Não encontrado');
});

app.listen(GAME_PORT, () => {
  console.log(`[game-server] servindo jogos isolados em http://localhost:${GAME_PORT}`);
});
