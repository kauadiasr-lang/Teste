// ============================================================================
// Gênese Infinita — motor do jogo
// ============================================================================

const LS_DESCOBERTOS = "genese_v1_descobertos";
const LS_GERADOS = "genese_v1_gerados";

/** @type {Set<string>} ids descobertos pelo jogador */
let descobertos = new Set(ELEMENTOS_BASE);

/** registro em runtime de elementos gerados dinamicamente (id -> dados) */
let gerados = {};

/** itens atualmente na mesa de trabalho: {uid, id, x, y} */
let boardItems = [];
let proximoUid = 1;

// ---------------------------------------------------------------------------
// Persistência
// ---------------------------------------------------------------------------
function carregarProgresso() {
  try {
    const salvos = JSON.parse(localStorage.getItem(LS_DESCOBERTOS) || "null");
    if (Array.isArray(salvos) && salvos.length) {
      descobertos = new Set(salvos);
    }
  } catch (e) { /* ignora dados corrompidos */ }

  try {
    const g = JSON.parse(localStorage.getItem(LS_GERADOS) || "null");
    if (g && typeof g === "object") gerados = g;
  } catch (e) { /* ignora */ }
}

function salvarDescobertos() {
  localStorage.setItem(LS_DESCOBERTOS, JSON.stringify([...descobertos]));
}

function salvarGerados() {
  localStorage.setItem(LS_GERADOS, JSON.stringify(gerados));
}

// ---------------------------------------------------------------------------
// Registro de elementos (estáticos + gerados dinamicamente)
// ---------------------------------------------------------------------------
function obterElemento(id) {
  return ELEMENTOS[id] || gerados[id] || null;
}

function obterOuCriarResultado(idA, idB) {
  const chave = chaveReceita(idA, idB);

  if (RECEITAS[chave]) {
    return RECEITAS[chave];
  }

  // já foi gerado antes nesta sessão/navegador?
  const existente = Object.entries(gerados).find(
    (entrada) => entrada[1]._origem === chave
  );
  if (existente) return existente[0];

  const candidato = gerarCombinacaoDesconhecida(idA, idB, obterElemento);

  if (gerados[candidato.id] || ELEMENTOS[candidato.id]) {
    // esse id já existe (alcançado por outro caminho) — reaproveita
    return candidato.id;
  }

  candidato._origem = chave;
  gerados[candidato.id] = candidato;
  salvarGerados();
  return candidato.id;
}

// ---------------------------------------------------------------------------
// UI: sidebar
// ---------------------------------------------------------------------------
const listaEl = document.getElementById("lista-elementos");
const buscaEl = document.getElementById("busca");
const contadorEl = document.getElementById("contador");

function renderSidebar() {
  const filtro = buscaEl.value.trim().toLowerCase();
  const itens = [...descobertos]
    .map((id) => ({ id, el: obterElemento(id) }))
    .filter((x) => x.el)
    .filter((x) => !filtro || x.el.nome.toLowerCase().includes(filtro))
    .sort((a, b) => a.el.nome.localeCompare(b.el.nome, "pt-BR"));

  listaEl.innerHTML = "";
  for (const { id, el } of itens) {
    const chip = document.createElement("div");
    chip.className = "chip" + (el.gerado ? " gerado" : "");
    chip.dataset.id = id;
    chip.innerHTML = `<span class="emoji">${el.emoji}</span><span>${el.nome}</span>`;
    chip.addEventListener("pointerdown", (ev) => iniciarArrasteDeNovo(ev, id));
    listaEl.appendChild(chip);
  }

  contadorEl.textContent = `${descobertos.size} descoberto${descobertos.size === 1 ? "" : "s"}`;
}

buscaEl.addEventListener("input", renderSidebar);

function marcarNovoNaSidebar(id) {
  requestAnimationFrame(() => {
    const chip = listaEl.querySelector(`.chip[data-id="${CSS.escape(id)}"]`);
    if (chip) {
      chip.classList.add("novo-flash");
      setTimeout(() => chip.classList.remove("novo-flash"), 1500);
    }
  });
}

// ---------------------------------------------------------------------------
// UI: toasts
// ---------------------------------------------------------------------------
const toastsEl = document.getElementById("toasts");

function mostrarToast(el, ehNovo) {
  const toast = document.createElement("div");
  toast.className = "toast" + (ehNovo ? "" : " duplicate");
  toast.innerHTML = `<span class="toast-emoji">${el.emoji}</span><span>${
    ehNovo ? `Novo: <b>${el.nome}</b>` : `${el.nome}`
  }</span>`;
  toastsEl.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// ---------------------------------------------------------------------------
// UI: mesa de trabalho (board)
// ---------------------------------------------------------------------------
const boardWrap = document.querySelector(".board-wrap");
const boardEl = document.getElementById("board");
const boardHint = document.getElementById("board-hint");

const LIMIAR_COMBINACAO = 50; // px de distância entre centros para combinar

function posicaoNoBoard(clientX, clientY) {
  const rect = boardEl.getBoundingClientRect();
  return {
    x: clientX - rect.left,
    y: clientY - rect.top,
  };
}

function renderBoardItem(item) {
  const el = obterElemento(item.id);
  const chip = document.createElement("div");
  chip.className = "board-chip";
  chip.dataset.uid = item.uid;
  chip.style.left = item.x + "px";
  chip.style.top = item.y + "px";
  chip.innerHTML = `<span class="emoji">${el.emoji}</span><span class="nome">${el.nome}</span><span class="remove-x">✕</span>`;

  chip.querySelector(".remove-x").addEventListener("pointerdown", (ev) => {
    ev.stopPropagation();
    removerDoBoard(item.uid);
  });

  chip.addEventListener("pointerdown", (ev) => {
    if (ev.target.classList.contains("remove-x")) return;
    iniciarArrasteExistente(ev, item.uid);
  });

  boardEl.appendChild(chip);
  return chip;
}

function atualizarDicaBoard() {
  boardHint.style.display = boardItems.length === 0 ? "block" : "none";
}

function removerDoBoard(uid) {
  boardItems = boardItems.filter((i) => i.uid !== uid);
  const chip = boardEl.querySelector(`.board-chip[data-uid="${uid}"]`);
  if (chip) chip.remove();
  atualizarDicaBoard();
}

function limparMesa() {
  boardItems = [];
  boardEl.querySelectorAll(".board-chip").forEach((c) => c.remove());
  atualizarDicaBoard();
}

function criarFaiscas(x, y) {
  for (let i = 0; i < 10; i++) {
    const spark = document.createElement("div");
    spark.className = "spark";
    const ang = (Math.PI * 2 * i) / 10;
    const dist = 30 + Math.random() * 20;
    spark.style.setProperty("--dx", Math.cos(ang) * dist + "px");
    spark.style.setProperty("--dy", Math.sin(ang) * dist + "px");
    spark.style.left = x + "px";
    spark.style.top = y + "px";
    boardEl.appendChild(spark);
    setTimeout(() => spark.remove(), 650);
  }
}

// ---- arraste: novo item vindo da sidebar -----------------------------------
function iniciarArrasteDeNovo(ev, id) {
  ev.preventDefault();
  const uid = proximoUid++;
  const pos = posicaoNoBoard(ev.clientX, ev.clientY);
  const item = { uid, id, x: pos.x, y: pos.y };
  boardItems.push(item);
  const chip = renderBoardItem(item);
  atualizarDicaBoard();
  chip.setPointerCapture(ev.pointerId);
  iniciarRastreamento(ev, chip, item);
}

// ---- arraste: item já existente no board -----------------------------------
function iniciarArrasteExistente(ev, uid) {
  ev.preventDefault();
  const item = boardItems.find((i) => i.uid === uid);
  if (!item) return;
  const chip = boardEl.querySelector(`.board-chip[data-uid="${uid}"]`);
  chip.setPointerCapture(ev.pointerId);
  boardEl.appendChild(chip); // traz para frente
  iniciarRastreamento(ev, chip, item);
}

function iniciarRastreamento(evInicial, chip, item) {
  chip.classList.add("dragging");
  const scrollEl = boardWrap;

  function aoMover(ev) {
    const pos = posicaoNoBoard(ev.clientX, ev.clientY);
    item.x = pos.x;
    item.y = pos.y;
    chip.style.left = item.x + "px";
    chip.style.top = item.y + "px";

    // destaca alvo próximo
    let alvo = encontrarAlvoProximo(item);
    boardEl.querySelectorAll(".board-chip.hover-target").forEach((c) => {
      if (!alvo || c.dataset.uid != alvo.uid) c.classList.remove("hover-target");
    });
    if (alvo) {
      const alvoChip = boardEl.querySelector(`.board-chip[data-uid="${alvo.uid}"]`);
      if (alvoChip) alvoChip.classList.add("hover-target");
    }
  }

  function aoSoltar(ev) {
    chip.classList.remove("dragging");
    scrollEl.removeEventListener("pointermove", aoMover);
    window.removeEventListener("pointerup", aoSoltar);
    window.removeEventListener("pointercancel", aoSoltar);

    const alvo = encontrarAlvoProximo(item);
    boardEl.querySelectorAll(".board-chip.hover-target").forEach((c) => c.classList.remove("hover-target"));

    if (alvo) {
      combinar(item, alvo, chip);
    }
  }

  window.addEventListener("pointermove", aoMover);
  window.addEventListener("pointerup", aoSoltar);
  window.addEventListener("pointercancel", aoSoltar);
}

function encontrarAlvoProximo(item) {
  let melhor = null;
  let melhorDist = LIMIAR_COMBINACAO;
  for (const outro of boardItems) {
    if (outro.uid === item.uid) continue;
    const dx = outro.x - item.x;
    const dy = outro.y - item.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < melhorDist) {
      melhorDist = dist;
      melhor = outro;
    }
  }
  return melhor;
}

function combinar(itemA, itemB, chipAEl) {
  const resultadoId = obterOuCriarResultado(itemA.id, itemB.id);
  const resultadoEl = obterElemento(resultadoId);
  const ehNovo = !descobertos.has(resultadoId);

  const midX = (itemA.x + itemB.x) / 2;
  const midY = (itemA.y + itemB.y) / 2;

  // remove os dois chips originais
  removerDoBoard(itemA.uid);
  removerDoBoard(itemB.uid);

  criarFaiscas(midX, midY);

  const novoUid = proximoUid++;
  const novoItem = { uid: novoUid, id: resultadoId, x: midX, y: midY };
  boardItems.push(novoItem);
  const novoChip = renderBoardItem(novoItem);
  novoChip.classList.add("spawn");
  atualizarDicaBoard();

  if (ehNovo) {
    descobertos.add(resultadoId);
    salvarDescobertos();
    renderSidebar();
    marcarNovoNaSidebar(resultadoId);
  }

  mostrarToast(resultadoEl, ehNovo);
}

// ---------------------------------------------------------------------------
// Ações de topo
// ---------------------------------------------------------------------------
document.getElementById("btn-limpar-mesa").addEventListener("click", limparMesa);

document.getElementById("btn-resetar").addEventListener("click", () => {
  if (confirm("Isso vai apagar todo o seu progresso (elementos descobertos). Tem certeza?")) {
    localStorage.removeItem(LS_DESCOBERTOS);
    localStorage.removeItem(LS_GERADOS);
    location.reload();
  }
});

const sidebarEl = document.getElementById("sidebar");
document.getElementById("btn-toggle-sidebar").addEventListener("click", () => {
  sidebarEl.classList.toggle("hidden");
});

// ---------------------------------------------------------------------------
// Início
// ---------------------------------------------------------------------------
carregarProgresso();
renderSidebar();
atualizarDicaBoard();
