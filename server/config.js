const APP_PORT = parseInt(process.env.APP_PORT || '3000', 10);
const GAME_PORT = parseInt(process.env.GAME_PORT || '4001', 10);

// Em produção isso deve ser dois domínios de verdade (ex: jogos.exemplo.com
// vs app.exemplo.com com subdomínios aleatórios por jogo), nunca a mesma
// origem do site principal. Em desenvolvimento local, usamos duas portas
// diferentes, o que já basta para a same-origin policy do navegador tratar
// como origens distintas — cookies e storage de uma não são visíveis pra outra.
const APP_ORIGIN = process.env.APP_ORIGIN || `http://localhost:${APP_PORT}`;
const GAME_ORIGIN = process.env.GAME_ORIGIN || `http://localhost:${GAME_PORT}`;

module.exports = { APP_PORT, GAME_PORT, APP_ORIGIN, GAME_ORIGIN };
