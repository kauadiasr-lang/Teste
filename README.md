# WebGames — MVP

Plataforma comunitária de jogos em HTML/CSS/JS: qualquer pessoa envia um
`.zip` com o jogo, ele passa por validação de segurança e fica jogável
direto no navegador, isolado numa origem separada.

Este é o MVP inicial, focado em resolver a parte mais arriscada do projeto
primeiro: rodar código de estranhos com segurança. Amizades, multiplayer e
autenticação ficam para as próximas fases (ver "Roadmap" abaixo).

## Como rodar

```bash
npm install
npm start
```

Isso sobe dois servidores:

- `http://localhost:3000` — site principal (listagem, upload, páginas)
- `http://localhost:4001` — servidor isolado que só serve os jogos

Abra `http://localhost:3000` no navegador.

## Arquitetura de segurança

O princípio geral: **nunca confie no conteúdo de um zip enviado por um
estranho**. Cada camada abaixo assume que a anterior pode falhar.

### 1. Origem separada para os jogos

O site principal roda na porta 3000, os jogos são servidos na porta 4001
por um processo Express completamente separado (`server/gameServer.js`).
Portas diferentes já contam como origens diferentes para a same-origin
policy do navegador — um jogo malicioso não consegue ler cookies, sessão
ou `localStorage` do site principal, porque tecnicamente está em outro
"site".

**Em produção**, troque portas por subdomínios de verdade (ex:
`jogos-usuario.suaplataforma.com` vs `app.suaplataforma.com`), idealmente
com um subdomínio/hash aleatório por jogo — é o mesmo padrão que
CodeSandbox e Glitch usam.

### 2. `<iframe sandbox>` mínimo

A página do jogo (`/game/:id`) carrega o jogo num
`<iframe sandbox="allow-scripts allow-pointer-lock">`. Note a ausência de
`allow-same-origin`: combinado com `allow-scripts` no mesmo domínio, isso
permitiria que o jogo removesse as próprias restrições do sandbox. Sem
`allow-same-origin`, mesmo que um bug futuro faça o iframe cair na mesma
origem do parent, o sandbox trata o conteúdo como uma origem opaca/nula.

### 3. Content-Security-Policy restrita nos jogos

Todo arquivo servido por `gameServer.js` sai com:

- `script-src 'self'` — nada de CDN externo ou script remoto
- `connect-src 'none'` — sem `fetch`/`XHR`/WebSocket (bloqueia exfiltração
  de dados; a fase de multiplayer vai abrir uma exceção pontual só para o
  servidor de relay)
- `object-src 'none'`, `form-action 'none'`, `base-uri 'none'`
- `frame-ancestors` travado só no domínio do site principal — ninguém mais
  pode embutir o jogo num iframe

### 4. Upload validado antes de qualquer escrita em disco

`server/validateZip.js` inspeciona **todas** as entradas do zip antes de
extrair a primeira. Rejeita:

- **Zip slip / path traversal**: nomes de arquivo com `..` ou caminho
  absoluto (testado — ver seção "O que foi testado")
- **Extensões não permitidas**: só html, css, js, imagens, áudio, fontes —
  nada de `.php`, `.exe`, scripts de servidor (testado)
- **Zip bomb**: limite de 50MB descomprimido no total, 10MB por arquivo, e
  checagem de razão de compressão suspeita
- **Ausência de `index.html`** na raiz do zip (testado)

Só depois de validar todas as entradas é que o código extrai para disco —
e ainda assim recalcula o caminho final e confirma que continua dentro do
diretório de destino (defesa em profundidade, redundante com a checagem
de nomes).

### 5. Sem execução no servidor

O zip vira arquivos estáticos. Não há `eval`, não há interpretador rodando
o conteúdo do usuário no back-end — só `express.static` servindo bytes.

### 6. Denúncia + moderação

Botão de "Denunciar" em cada jogo (`/api/games/:id/report`) e um painel
`/admin.html` que lista jogos por número de denúncias, com opção de
remover. Cobre o que validação automática não pega (conteúdo ofensivo,
mas não tecnicamente malicioso).

## O que foi testado manualmente

Antes deste commit, o pipeline de upload foi testado end-to-end com:

- Jogo válido → publica, aparece na listagem, roda no iframe isolado,
  headers de CSP corretos na resposta
- Zip sem `index.html` → rejeitado com erro claro, nada extraído
- Zip com `.php` disfarçado de asset → rejeitado, nada extraído
- Zip com entrada `../../etc/evil.js` (zip slip) → rejeitado, nada extraído
- Título contendo `<script>alert(1)</script>` → escapado corretamente na
  página renderizada no servidor (`/game/:id`); a listagem usa
  `textContent` no client, então também não interpreta o valor como HTML
- Remoção via painel admin → apaga do banco e do disco

## Limitações conhecidas (não é produção)

- **Sem autenticação** em lugar nenhum, incluindo `/admin.html` e
  `DELETE /api/games/:id`. Antes de expor isto publicamente, isso *precisa*
  ficar atrás de login.
- **Armazenamento em arquivo JSON** (`data/db.json`), sem controle de
  concorrência — ok para demo, não para tráfego real. Trocar por Postgres
  ou similar antes de produção.
- **Rate limiting inexistente**: nada impede um usuário de subir 1000 zips
  por minuto. Adicionar antes de abrir ao público.
- **Sem varredura de malware/conteúdo**: os testes cobrem os vetores
  técnicos óbvios (path traversal, extensão, zip bomb), mas não
  substituem um scanner de verdade nem moderação humana para conteúdo
  impróprio.
- **CSP dos jogos permite `'unsafe-inline'`** em script/style para não
  quebrar jogos simples que usam `<script>` inline. Isso é uma concessão
  deliberada: ainda bloqueia scripts de origem externa e `eval`, mas é
  mais fraco que uma CSP com nonces. Ideal para v2.

## Roadmap (não implementado ainda)

1. **SDK de multiplayer via `postMessage`**: um `platform.js` que o jogo
   importa, com `createRoom()` / `onPlayerJoin()` / `broadcast()`, falando
   com um servidor de relay via WebSocket. A CSP dos jogos abriria
   `connect-src` só para esse relay, nunca para rede livre.
2. **Contas e amizades**: autenticação real, lista de amigos, convite para
   jogar.
3. **Rate limiting e quotas** de upload por usuário.
4. **Scanner automático** de padrões maliciosos conhecidos no upload.

## Estrutura do projeto

```
server/
  index.js        site principal: listagem, upload, páginas, admin
  gameServer.js   servidor isolado que só serve os jogos extraídos
  validateZip.js  validação de segurança do zip (a peça mais crítica)
  db.js           armazenamento simples em JSON
  config.js       portas/origens (via variáveis de ambiente)
  start.js        sobe os dois servidores juntos em dev
public/           site principal (HTML/CSS/JS simples, sem build step)
games/            jogos extraídos (gerado em runtime, fora do git)
data/             db.json (gerado em runtime, fora do git)
```
