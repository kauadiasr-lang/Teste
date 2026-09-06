// Conveniência para rodar os dois servidores (site principal + jogos
// isolados) com um único comando em desenvolvimento. Em produção, rode-os
// como serviços separados de verdade (processos/containers distintos).
const { spawn } = require('child_process');
const path = require('path');

function run(name, file) {
  const child = spawn(process.execPath, [path.join(__dirname, file)], {
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  child.stdout.on('data', (d) => process.stdout.write(`[${name}] ${d}`));
  child.stderr.on('data', (d) => process.stderr.write(`[${name}] ${d}`));
  child.on('exit', (code) => {
    console.log(`[${name}] encerrou com código ${code}`);
  });
  return child;
}

const app = run('app', 'index.js');
const games = run('games', 'gameServer.js');

process.on('SIGINT', () => {
  app.kill();
  games.kill();
  process.exit(0);
});
